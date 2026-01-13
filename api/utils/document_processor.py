"""
Utility functions for document processing, chunking, and text extraction
"""
import re
import os
from typing import List, Tuple
import PyPDF2
import pdfplumber
import markdown
from docx import Document as DocxDocument


class DocumentProcessor:
    """
    Process different document types and extract text
    """
    
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> List[Tuple[str, int]]:
        """
        Extract text from PDF file
        Returns: List of tuples (text, page_number)
        """
        pages_content = []
        
        try:
            # Try with pdfplumber first (better for complex PDFs)
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    text = page.extract_text()
                    if text and text.strip():
                        pages_content.append((text, page_num))
        except Exception as e:
            # Fallback to PyPDF2
            try:
                with open(file_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    for page_num, page in enumerate(reader.pages, start=1):
                        text = page.extract_text()
                        if text and text.strip():
                            pages_content.append((text, page_num))
            except Exception as inner_e:
                raise Exception(f"Failed to extract PDF text: {str(inner_e)}")
        
        return pages_content
    
    @staticmethod
    def extract_text_from_markdown(file_path: str) -> str:
        """
        Extract text from Markdown file
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            # Convert markdown to plain text (remove markdown syntax)
            html = markdown.markdown(content)
            # Remove HTML tags
            text = re.sub(r'<[^>]+>', '', html)
            return text
    
    @staticmethod
    def extract_text_from_txt(file_path: str) -> str:
        """
        Extract text from plain text file
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        """
        Extract text from DOCX file
        """
        doc = DocxDocument(file_path)
        full_text = []
        for paragraph in doc.paragraphs:
            full_text.append(paragraph.text)
        return '\n'.join(full_text)
    
    @classmethod
    def process_document(cls, file_path: str, file_type: str) -> List[Tuple[str, int]]:
        """
        Process document based on file type
        Returns: List of tuples (text, page_number) for PDFs, or [(text, 1)] for others
        """
        file_type = file_type.lower()
        
        if file_type == 'pdf':
            return cls.extract_text_from_pdf(file_path)
        elif file_type in ['md', 'markdown']:
            text = cls.extract_text_from_markdown(file_path)
            return [(text, 1)]
        elif file_type == 'txt':
            text = cls.extract_text_from_txt(file_path)
            return [(text, 1)]
        elif file_type == 'docx':
            text = cls.extract_text_from_docx(file_path)
            return [(text, 1)]
        else:
            raise ValueError(f"Unsupported file type: {file_type}")


class TextChunker:
    """
    Split text into semantic chunks for embedding
    """
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.,!?;:()\-\']', '', text)
        return text.strip()
    
    def split_by_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences
        """
        # Simple sentence splitter (can be improved with nltk or spacy)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def create_chunks(self, text: str, page_number: int = 1) -> List[dict]:
        """
        Create overlapping chunks from text
        Returns: List of dicts with 'content', 'page_number', 'chunk_index'
        """
        cleaned_text = self.clean_text(text)
        sentences = self.split_by_sentences(cleaned_text)
        
        chunks = []
        current_chunk = []
        current_size = 0
        chunk_index = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            # If adding this sentence exceeds chunk size, save current chunk
            if current_size + sentence_length > self.chunk_size and current_chunk:
                chunk_text = ' '.join(current_chunk)
                chunks.append({
                    'content': chunk_text,
                    'page_number': page_number,
                    'chunk_index': chunk_index
                })
                chunk_index += 1
                
                # Keep last few sentences for overlap
                overlap_text = chunk_text[-self.chunk_overlap:]
                overlap_sentences = self.split_by_sentences(overlap_text)
                current_chunk = overlap_sentences
                current_size = len(overlap_text)
            
            current_chunk.append(sentence)
            current_size += sentence_length
        
        # Add remaining chunk
        if current_chunk:
            chunks.append({
                'content': ' '.join(current_chunk),
                'page_number': page_number,
                'chunk_index': chunk_index
            })
        
        return chunks
    
    def chunk_document(self, pages_content: List[Tuple[str, int]]) -> List[dict]:
        """
        Chunk entire document
        """
        all_chunks = []
        global_chunk_index = 0
        
        for text, page_number in pages_content:
            page_chunks = self.create_chunks(text, page_number)
            for chunk in page_chunks:
                chunk['chunk_index'] = global_chunk_index
                all_chunks.append(chunk)
                global_chunk_index += 1
        
        return all_chunks
