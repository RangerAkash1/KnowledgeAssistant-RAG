"""
RAG (Retrieval-Augmented Generation) system with LLM integration
"""
import time
from typing import List, Dict, Tuple
import openai
from django.conf import settings
from django.core.cache import cache
import hashlib
import json


class LLMProvider:
    """
    LLM provider for generating responses
    """
    
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        openai.api_key = self.api_key
    
    def generate_response(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        Generate response from LLM
        """
        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful knowledge assistant. Answer questions based ONLY on the provided context. If the context doesn't contain enough information to answer the question, say so explicitly. Do not make up information or use external knowledge."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"LLM generation error: {str(e)}")


class PromptEngineer:
    """
    Construct optimized prompts for RAG
    """
    
    @staticmethod
    def construct_rag_prompt(question: str, context_chunks: List[Dict]) -> str:
        """
        Construct RAG prompt with retrieved context
        """
        # Build context section
        context_parts = []
        for i, chunk in enumerate(context_chunks, 1):
            source_info = f"[Source: {chunk['document_title']}"
            if chunk['page_number']:
                source_info += f" - Page {chunk['page_number']}"
            source_info += "]"
            
            context_parts.append(
                f"Context {i} {source_info}:\n{chunk['content']}\n"
            )
        
        context_text = "\n".join(context_parts)
        
        # Construct final prompt with clear instructions
        prompt = f"""Based on the following context from the knowledge base, please answer the question.

IMPORTANT INSTRUCTIONS:
1. Use ONLY the information provided in the context below
2. If the context doesn't contain enough information, explicitly state: "I don't have enough information in the knowledge base to answer this question."
3. Cite which source (Context 1, 2, etc.) you're using for each part of your answer
4. Be concise and accurate
5. Do not make assumptions or use external knowledge

CONTEXT:
{context_text}

QUESTION: {question}

ANSWER:"""
        
        return prompt
    
    @staticmethod
    def construct_no_context_response() -> str:
        """
        Response when no relevant context is found
        """
        return "I couldn't find any relevant information in the knowledge base to answer your question. Please try rephrasing your question or ensure that the relevant documents have been uploaded."


class RAGSystem:
    """
    Complete RAG system combining retrieval and generation
    """
    
    def __init__(self, vector_db):
        self.vector_db = vector_db
        self.llm = LLMProvider()
        self.prompt_engineer = PromptEngineer()
    
    def generate_cache_key(self, question: str, max_chunks: int) -> str:
        """
        Generate cache key for query
        """
        query_hash = hashlib.md5(
            f"{question.lower().strip()}_{max_chunks}".encode()
        ).hexdigest()
        return f"rag_query_{query_hash}"
    
    def answer_question(
        self,
        question: str,
        max_chunks: int = 5,
        temperature: float = 0.7,
        use_cache: bool = True
    ) -> Dict:
        """
        Answer question using RAG
        
        Returns:
            {
                'answer': str,
                'sources': List[str],
                'confidence': float,
                'processing_time': float,
                'cached': bool,
                'retrieved_chunks': int
            }
        """
        start_time = time.time()
        
        # Check cache
        cache_key = self.generate_cache_key(question, max_chunks)
        if use_cache:
            cached_result = cache.get(cache_key)
            if cached_result:
                cached_result['cached'] = True
                cached_result['processing_time'] = time.time() - start_time
                return cached_result
        
        # Step 1: Retrieve relevant chunks
        retrieved_chunks = self.vector_db.search(question, top_k=max_chunks)
        
        # Step 2: Check if we have relevant context
        if not retrieved_chunks:
            result = {
                'answer': self.prompt_engineer.construct_no_context_response(),
                'sources': [],
                'confidence': 0.0,
                'processing_time': time.time() - start_time,
                'cached': False,
                'retrieved_chunks': 0
            }
            return result
        
        # Filter chunks by minimum similarity threshold
        min_similarity = 0.3
        relevant_chunks = [
            chunk for chunk in retrieved_chunks
            if chunk['similarity_score'] >= min_similarity
        ]
        
        if not relevant_chunks:
            result = {
                'answer': self.prompt_engineer.construct_no_context_response(),
                'sources': [],
                'confidence': 0.0,
                'processing_time': time.time() - start_time,
                'cached': False,
                'retrieved_chunks': len(retrieved_chunks)
            }
            return result
        
        # Step 3: Construct prompt
        prompt = self.prompt_engineer.construct_rag_prompt(question, relevant_chunks)
        
        # Step 4: Generate answer
        try:
            answer = self.llm.generate_response(prompt, temperature=temperature)
        except Exception as e:
            result = {
                'answer': f"Error generating response: {str(e)}",
                'sources': [],
                'confidence': 0.0,
                'processing_time': time.time() - start_time,
                'cached': False,
                'retrieved_chunks': len(relevant_chunks)
            }
            return result
        
        # Step 5: Prepare sources
        sources = []
        for chunk in relevant_chunks:
            source = chunk['document_title']
            if chunk['page_number']:
                source += f" - Page {chunk['page_number']}"
            if source not in sources:
                sources.append(source)
        
        # Calculate confidence based on similarity scores
        avg_similarity = sum(c['similarity_score'] for c in relevant_chunks) / len(relevant_chunks)
        confidence = min(avg_similarity * 1.2, 1.0)  # Scale up slightly, cap at 1.0
        
        # Prepare result
        result = {
            'answer': answer,
            'sources': sources,
            'confidence': round(confidence, 2),
            'processing_time': time.time() - start_time,
            'cached': False,
            'retrieved_chunks': len(relevant_chunks)
        }
        
        # Cache result
        if use_cache:
            cache.set(cache_key, result, timeout=3600)  # Cache for 1 hour
        
        return result
    
    def clear_cache(self) -> None:
        """
        Clear all cached queries
        """
        cache.clear()
