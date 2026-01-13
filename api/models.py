"""
Database models for Knowledge Assistant
"""
from django.db import models
from django.utils import timezone


class Document(models.Model):
    """
    Model to store uploaded documents metadata
    """
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='documents/')
    file_type = models.CharField(max_length=50)
    file_size = models.IntegerField()  # in bytes
    
    # Processing status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Metadata
    num_chunks = models.IntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return self.title


class DocumentChunk(models.Model):
    """
    Model to store individual text chunks from documents
    """
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='chunks')
    content = models.TextField()
    chunk_index = models.IntegerField()
    page_number = models.IntegerField(null=True, blank=True)
    
    # Embedding metadata
    embedding_vector = models.BinaryField(null=True, blank=True)  # Serialized numpy array
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['document', 'chunk_index']
        unique_together = ['document', 'chunk_index']
    
    def __str__(self):
        return f"{self.document.title} - Chunk {self.chunk_index}"


class QueryHistory(models.Model):
    """
    Model to store query history and responses
    """
    question = models.TextField()
    answer = models.TextField()
    sources = models.JSONField(default=list)
    
    # Metadata
    retrieved_chunks_count = models.IntegerField(default=0)
    processing_time = models.FloatField()  # in seconds
    confidence_score = models.FloatField(null=True, blank=True)
    
    # Caching
    cache_hit = models.BooleanField(default=False)

    # Access metadata
    user_token = models.CharField(max_length=255, null=True, blank=True)
    client_ip = models.GenericIPAddressField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Query histories"
    
    def __str__(self):
        return f"Query: {self.question[:50]}..."
