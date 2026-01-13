"""
API Views for Knowledge Assistant
"""
import os
import time
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings

from .models import Document, DocumentChunk, QueryHistory
from .serializers import (
    DocumentSerializer,
    DocumentUploadSerializer,
    BulkDocumentUploadSerializer,
    QuestionSerializer,
    AnswerSerializer,
    QueryHistorySerializer
)
from .utils.document_processor import DocumentProcessor, TextChunker
from .utils.vector_db import vector_db
from .utils.rag_system import RAGSystem


# Initialize RAG system
rag_system = RAGSystem(vector_db)


def _is_authorized(request):
    """
    Simple token-based access control. If API_TOKEN is set in settings,
    require header Authorization: Token <API_TOKEN>
    """
    token = getattr(settings, 'API_TOKEN', '')
    if not token:
        return True  # token not configured, allow all
    auth_header = request.headers.get('Authorization') or ''
    if auth_header.startswith('Token '):
        provided = auth_header.replace('Token ', '', 1).strip()
        return provided == token
    return False


class DocumentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing documents
    """
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    
    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload(self, request):
        """
        Upload and process a document
        POST /api/documents/upload/
        """
        if not _is_authorized(request):
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = DocumentUploadSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        file = serializer.validated_data['file']
        title = serializer.validated_data['title']
        description = serializer.validated_data.get('description', '')
        
        # Get file type
        file_ext = file.name.split('.')[-1].lower()
        
        # Create document record
        document = Document.objects.create(
            title=title,
            description=description,
            file=file,
            file_type=file_ext,
            file_size=file.size,
            status='processing'
        )
        
        try:
            # Process document
            file_path = document.file.path
            
            # Extract text
            processor = DocumentProcessor()
            pages_content = processor.process_document(file_path, file_ext)
            
            # Chunk text
            chunker = TextChunker(
                chunk_size=settings.CHUNK_SIZE,
                chunk_overlap=settings.CHUNK_OVERLAP
            )
            chunks = chunker.chunk_document(pages_content)
            
            # Save chunks to database
            chunk_objects = []
            for chunk_data in chunks:
                chunk_obj = DocumentChunk.objects.create(
                    document=document,
                    content=chunk_data['content'],
                    chunk_index=chunk_data['chunk_index'],
                    page_number=chunk_data['page_number']
                )
                chunk_objects.append(chunk_obj)
            
            # Add to vector database
            vector_chunks = [
                {
                    'id': chunk.id,
                    'content': chunk.content,
                    'document_id': document.id,
                    'document_title': document.title,
                    'page_number': chunk.page_number,
                    'chunk_index': chunk.chunk_index
                }
                for chunk in chunk_objects
            ]
            vector_db.add_documents(vector_chunks)
            
            # Update document status
            document.status = 'completed'
            document.num_chunks = len(chunks)
            document.save()
            
            return Response(
                {
                    'message': 'Document uploaded and processed successfully',
                    'document': DocumentSerializer(document).data
                },
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            # Update document status to failed
            document.status = 'failed'
            document.save()
            
            return Response(
                {'error': f'Failed to process document: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_bulk(self, request):
        """
        Upload and process multiple documents in one request
        POST /api/documents/upload_bulk/
        """
        if not _is_authorized(request):
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = BulkDocumentUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        files = serializer.validated_data['files']
        description = serializer.validated_data.get('description', '')
        results = []

        for file_obj in files:
            title = file_obj.name
            file_ext = file_obj.name.split('.')[-1].lower()

            document = Document.objects.create(
                title=title,
                description=description,
                file=file_obj,
                file_type=file_ext,
                file_size=file_obj.size,
                status='processing'
            )

            try:
                processor = DocumentProcessor()
                pages_content = processor.process_document(document.file.path, file_ext)

                chunker = TextChunker(
                    chunk_size=settings.CHUNK_SIZE,
                    chunk_overlap=settings.CHUNK_OVERLAP
                )
                chunks = chunker.chunk_document(pages_content)

                chunk_objects = []
                for chunk_data in chunks:
                    chunk_obj = DocumentChunk.objects.create(
                        document=document,
                        content=chunk_data['content'],
                        chunk_index=chunk_data['chunk_index'],
                        page_number=chunk_data['page_number']
                    )
                    chunk_objects.append(chunk_obj)

                vector_chunks = [
                    {
                        'id': chunk.id,
                        'content': chunk.content,
                        'document_id': document.id,
                        'document_title': document.title,
                        'page_number': chunk.page_number,
                        'chunk_index': chunk.chunk_index
                    }
                    for chunk in chunk_objects
                ]
                vector_db.add_documents(vector_chunks)

                document.status = 'completed'
                document.num_chunks = len(chunks)
                document.save()

                results.append({'document': DocumentSerializer(document).data, 'status': 'ok'})
            except Exception as e:
                document.status = 'failed'
                document.save()
                results.append({'document': DocumentSerializer(document).data, 'status': 'failed', 'error': str(e)})

        return Response({'results': results}, status=status.HTTP_201_CREATED)
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete a document and its chunks from vector database
        """
        document = self.get_object()
        document_id = document.id
        
        # Remove from vector database
        try:
            vector_db.remove_document_chunks(document_id)
        except Exception as e:
            print(f"Error removing document from vector DB: {e}")
        
        # Delete document (cascades to chunks)
        document.delete()
        
        return Response(
            {'message': 'Document deleted successfully'},
            status=status.HTTP_204_NO_CONTENT
        )


@api_view(['POST'])
def ask_question(request):
    """
    Answer a question using RAG
    POST /api/ask-question/
    
    Request body:
    {
        "question": "What is the use of mitochondria?",
        "max_chunks": 5,  # optional
        "temperature": 0.7  # optional
    }
    """
    serializer = QuestionSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    question = serializer.validated_data['question']
    max_chunks = serializer.validated_data.get('max_chunks', settings.MAX_RETRIEVED_CHUNKS)
    temperature = serializer.validated_data.get('temperature', settings.TEMPERATURE)
    
    try:
        # Generate answer using RAG
        result = rag_system.answer_question(
            question=question,
            max_chunks=max_chunks,
            temperature=temperature,
            use_cache=True
        )
        
        # Save to query history
        QueryHistory.objects.create(
            question=question,
            answer=result['answer'],
            sources=result['sources'],
            retrieved_chunks_count=result['retrieved_chunks'],
            processing_time=result['processing_time'],
            confidence_score=result['confidence'],
            cache_hit=result['cached'],
            user_token=request.headers.get('Authorization'),
            client_ip=request.META.get('REMOTE_ADDR')
        )
        
        # Prepare response
        response_serializer = AnswerSerializer(data=result)
        if response_serializer.is_valid():
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        
        return Response(result, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to generate answer: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def query_history(request):
    """
    Get query history
    GET /api/query-history/
    """
    queries = QueryHistory.objects.all()[:50]  # Last 50 queries
    serializer = QueryHistorySerializer(queries, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def clear_cache(request):
    """
    Clear query cache
    POST /api/clear-cache/
    """
    try:
        rag_system.clear_cache()
        return Response(
            {'message': 'Cache cleared successfully'},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to clear cache: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def system_stats(request):
    """
    Get system statistics
    GET /api/stats/
    """
    stats = {
        'total_documents': Document.objects.count(),
        'processed_documents': Document.objects.filter(status='completed').count(),
        'total_chunks': DocumentChunk.objects.count(),
        'total_queries': QueryHistory.objects.count(),
        'vector_db_size': vector_db.index.ntotal,
        'cache_hits': QueryHistory.objects.filter(cache_hit=True).count(),
    }
    return Response(stats)
