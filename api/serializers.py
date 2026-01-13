"""
Serializers for API endpoints
"""
from rest_framework import serializers
from .models import Document, DocumentChunk, QueryHistory


class DocumentSerializer(serializers.ModelSerializer):
    """
    Serializer for Document model
    """
    class Meta:
        model = Document
        fields = [
            'id', 'title', 'description', 'file', 'file_type', 
            'file_size', 'status', 'num_chunks', 'uploaded_at', 
            'processed_at'
        ]
        read_only_fields = ['id', 'file_type', 'file_size', 'status', 
                           'num_chunks', 'uploaded_at', 'processed_at']


class DocumentUploadSerializer(serializers.Serializer):
    """
    Serializer for document upload
    """
    file = serializers.FileField()
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    
    def validate_file(self, value):
        """
        Validate uploaded file
        """
        # Check file extension
        allowed_extensions = ['.pdf', '.md', '.txt', '.docx']
        file_ext = value.name.split('.')[-1].lower()
        if f'.{file_ext}' not in allowed_extensions:
            raise serializers.ValidationError(
                f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Check file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if value.size > max_size:
            raise serializers.ValidationError(
                f"File size exceeds maximum allowed size of 10MB"
            )
        
        return value


class BulkDocumentUploadSerializer(serializers.Serializer):
    """
    Serializer for uploading multiple documents at once
    """
    files = serializers.ListField(
        child=serializers.FileField(), allow_empty=False
    )
    description = serializers.CharField(required=False, allow_blank=True)

    def validate_files(self, value):
        allowed_extensions = ['.pdf', '.md', '.txt', '.docx']
        max_size = 10 * 1024 * 1024  # 10MB

        for file_obj in value:
            file_ext = file_obj.name.split('.')[-1].lower()
            if f'.{file_ext}' not in allowed_extensions:
                raise serializers.ValidationError(
                    f"Unsupported file type {file_obj.name}. Allowed: {', '.join(allowed_extensions)}"
                )
            if file_obj.size > max_size:
                raise serializers.ValidationError(
                    f"File {file_obj.name} exceeds maximum allowed size of 10MB"
                )
        return value


class QuestionSerializer(serializers.Serializer):
    """
    Serializer for question input
    """
    question = serializers.CharField(required=True)
    max_chunks = serializers.IntegerField(required=False, default=5, min_value=1, max_value=10)
    temperature = serializers.FloatField(required=False, default=0.7, min_value=0, max_value=2)


class AnswerSerializer(serializers.Serializer):
    """
    Serializer for answer response
    """
    answer = serializers.CharField()
    sources = serializers.ListField(child=serializers.CharField())
    confidence = serializers.FloatField(required=False)
    processing_time = serializers.FloatField(required=False)
    cached = serializers.BooleanField(required=False, default=False)


class QueryHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for QueryHistory model
    """
    class Meta:
        model = QueryHistory
        fields = '__all__'
