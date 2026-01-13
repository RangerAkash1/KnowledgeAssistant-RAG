"""
Tests for Knowledge Assistant API
"""
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from .models import Document, DocumentChunk, QueryHistory


class DocumentUploadTestCase(TestCase):
    """
    Test document upload functionality
    """
    
    def setUp(self):
        self.client = APIClient()
    
    def test_upload_text_document(self):
        """
        Test uploading a text document
        """
        content = b"This is a test document about mitochondria. The mitochondria is the powerhouse of the cell."
        file = SimpleUploadedFile("test.txt", content, content_type="text/plain")
        
        response = self.client.post(
            '/api/documents/upload/',
            {
                'file': file,
                'title': 'Test Document',
                'description': 'A test document'
            },
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Document.objects.count(), 1)
    
    def test_list_documents(self):
        """
        Test listing documents
        """
        response = self.client.get('/api/documents/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class QuestionAnsweringTestCase(TestCase):
    """
    Test question answering functionality
    """
    
    def setUp(self):
        self.client = APIClient()
    
    def test_ask_question_no_context(self):
        """
        Test asking a question with no documents
        """
        response = self.client.post(
            '/api/ask-question/',
            {
                'question': 'What is mitochondria?'
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('answer', response.data)
