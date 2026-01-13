"""
Vector database management using FAISS and embeddings
"""
import os
import pickle
import numpy as np
from typing import List, Dict, Tuple
import faiss
from sentence_transformers import SentenceTransformer
from django.conf import settings
import openai


class EmbeddingGenerator:
    """
    Generate embeddings for text using OpenAI or Sentence Transformers
    """
    
    def __init__(self, use_openai: bool = True):
        self.use_openai = use_openai and bool(settings.OPENAI_API_KEY)
        
        if self.use_openai:
            openai.api_key = settings.OPENAI_API_KEY
            self.embedding_model = settings.EMBEDDING_MODEL
            self.embedding_dim = 1536  # OpenAI ada-002 dimension
        else:
            # Fallback to sentence-transformers
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.embedding_dim = 384  # MiniLM dimension
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text
        """
        if self.use_openai:
            try:
                response = openai.embeddings.create(
                    model=self.embedding_model,
                    input=text
                )
                return np.array(response.data[0].embedding, dtype=np.float32)
            except Exception as e:
                print(f"OpenAI API error: {e}. Falling back to sentence-transformers.")
                # Fallback to local model
                if not hasattr(self, 'model'):
                    self.model = SentenceTransformer('all-MiniLM-L6-v2')
                return self.model.encode(text, convert_to_numpy=True).astype(np.float32)
        else:
            return self.model.encode(text, convert_to_numpy=True).astype(np.float32)
    
    def generate_embeddings_batch(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for multiple texts
        """
        if self.use_openai:
            embeddings = []
            # Process in batches to avoid rate limits
            batch_size = 100
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                try:
                    response = openai.embeddings.create(
                        model=self.embedding_model,
                        input=batch
                    )
                    batch_embeddings = [item.embedding for item in response.data]
                    embeddings.extend(batch_embeddings)
                except Exception as e:
                    print(f"OpenAI batch error: {e}. Processing individually.")
                    for text in batch:
                        embeddings.append(self.generate_embedding(text))
            return np.array(embeddings, dtype=np.float32)
        else:
            return self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True).astype(np.float32)


class VectorDatabase:
    """
    FAISS-based vector database for semantic search
    """
    
    def __init__(self, embedding_dim: int = None):
        self.embedding_generator = EmbeddingGenerator()
        self.embedding_dim = embedding_dim or self.embedding_generator.embedding_dim
        
        # Initialize FAISS index
        self.index = faiss.IndexFlatL2(self.embedding_dim)  # L2 distance
        # Optionally use IndexIVFFlat for larger datasets
        
        # Metadata storage (chunk_id -> metadata)
        self.metadata = {}
        self.chunk_id_to_index = {}
        self.index_to_chunk_id = {}
        
        self.vector_db_path = settings.VECTOR_DB_PATH
        self.index_file = os.path.join(self.vector_db_path, 'faiss_index.bin')
        self.metadata_file = os.path.join(self.vector_db_path, 'metadata.pkl')
        
        # Load existing index if available
        self.load()
    
    def add_documents(self, chunks: List[Dict]) -> None:
        """
        Add document chunks to vector database
        chunks: List of dicts with 'id', 'content', 'document_title', 'page_number'
        """
        if not chunks:
            return
        
        texts = [chunk['content'] for chunk in chunks]
        embeddings = self.embedding_generator.generate_embeddings_batch(texts)
        
        # Add to FAISS index
        start_idx = self.index.ntotal
        self.index.add(embeddings)
        
        # Store metadata
        for i, chunk in enumerate(chunks):
            chunk_id = chunk['id']
            index_position = start_idx + i
            
            self.metadata[chunk_id] = {
                'content': chunk['content'],
                'document_id': chunk.get('document_id'),
                'document_title': chunk.get('document_title'),
                'page_number': chunk.get('page_number'),
                'chunk_index': chunk.get('chunk_index'),
            }
            self.chunk_id_to_index[chunk_id] = index_position
            self.index_to_chunk_id[index_position] = chunk_id
        
        # Save after adding
        self.save()
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search for similar chunks
        Returns: List of dicts with chunk metadata and similarity score
        """
        if self.index.ntotal == 0:
            return []
        
        # Generate query embedding
        query_embedding = self.embedding_generator.generate_embedding(query)
        query_embedding = query_embedding.reshape(1, -1)
        
        # Search FAISS index
        distances, indices = self.index.search(query_embedding, min(top_k, self.index.ntotal))
        
        # Prepare results
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:  # FAISS returns -1 for empty results
                continue
            
            chunk_id = self.index_to_chunk_id.get(idx)
            if chunk_id:
                metadata = self.metadata.get(chunk_id, {})
                results.append({
                    'chunk_id': chunk_id,
                    'content': metadata.get('content', ''),
                    'document_title': metadata.get('document_title', ''),
                    'page_number': metadata.get('page_number'),
                    'similarity_score': float(1 / (1 + dist)),  # Convert distance to similarity
                    'distance': float(dist)
                })
        
        return results

    def add_multiple_documents(self, documents_chunks: List[List[Dict]]) -> None:
        """
        Add multiple documents' chunks in one call
        documents_chunks: list where each item is list of chunks for a document
        """
        flat_chunks = []
        for doc_chunks in documents_chunks:
            flat_chunks.extend(doc_chunks)
        self.add_documents(flat_chunks)
    
    def remove_document_chunks(self, document_id: int) -> None:
        """
        Remove all chunks belonging to a document
        Note: FAISS doesn't support removal, so we need to rebuild the index
        """
        # Find chunks to remove
        chunks_to_remove = [
            chunk_id for chunk_id, meta in self.metadata.items()
            if meta.get('document_id') == document_id
        ]
        
        if not chunks_to_remove:
            return
        
        # Remove from metadata
        for chunk_id in chunks_to_remove:
            if chunk_id in self.metadata:
                del self.metadata[chunk_id]
            if chunk_id in self.chunk_id_to_index:
                del self.chunk_id_to_index[chunk_id]
        
        # Rebuild index (FAISS doesn't support deletion)
        self.rebuild_index()
    
    def rebuild_index(self) -> None:
        """
        Rebuild the entire FAISS index from metadata
        """
        # Create new index
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.index_to_chunk_id = {}
        self.chunk_id_to_index = {}
        
        if not self.metadata:
            return
        
        # Re-add all chunks
        chunks = []
        for chunk_id, meta in self.metadata.items():
            chunks.append({
                'id': chunk_id,
                'content': meta['content'],
                'document_id': meta.get('document_id'),
                'document_title': meta.get('document_title'),
                'page_number': meta.get('page_number'),
                'chunk_index': meta.get('chunk_index'),
            })
        
        if chunks:
            self.add_documents(chunks)
    
    def save(self) -> None:
        """
        Save FAISS index and metadata to disk
        """
        os.makedirs(self.vector_db_path, exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, self.index_file)
        
        # Save metadata
        with open(self.metadata_file, 'wb') as f:
            pickle.dump({
                'metadata': self.metadata,
                'chunk_id_to_index': self.chunk_id_to_index,
                'index_to_chunk_id': self.index_to_chunk_id
            }, f)
    
    def load(self) -> None:
        """
        Load FAISS index and metadata from disk
        """
        if os.path.exists(self.index_file) and os.path.exists(self.metadata_file):
            try:
                # Load FAISS index
                self.index = faiss.read_index(self.index_file)
                
                # Load metadata
                with open(self.metadata_file, 'rb') as f:
                    data = pickle.load(f)
                    self.metadata = data['metadata']
                    self.chunk_id_to_index = data['chunk_id_to_index']
                    self.index_to_chunk_id = data['index_to_chunk_id']
                
                print(f"Loaded vector database with {self.index.ntotal} vectors")
            except Exception as e:
                print(f"Error loading vector database: {e}")
                # Initialize empty index
                self.index = faiss.IndexFlatL2(self.embedding_dim)
    
    def clear(self) -> None:
        """
        Clear entire vector database
        """
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.metadata = {}
        self.chunk_id_to_index = {}
        self.index_to_chunk_id = {}
        self.save()


# Global vector database instance
vector_db = VectorDatabase()
