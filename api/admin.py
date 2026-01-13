from django.contrib import admin
from .models import Document, DocumentChunk, QueryHistory


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'file_type', 'status', 'num_chunks', 'uploaded_at']
    list_filter = ['status', 'file_type', 'uploaded_at']
    search_fields = ['title', 'description']
    readonly_fields = ['uploaded_at', 'processed_at', 'file_size', 'num_chunks']


@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ['document', 'chunk_index', 'page_number', 'created_at']
    list_filter = ['document', 'created_at']
    search_fields = ['content']
    readonly_fields = ['created_at']


@admin.register(QueryHistory)
class QueryHistoryAdmin(admin.ModelAdmin):
    list_display = ['question_preview', 'processing_time', 'cache_hit', 'created_at']
    list_filter = ['cache_hit', 'created_at']
    search_fields = ['question', 'answer']
    readonly_fields = ['created_at']
    
    def question_preview(self, obj):
        return obj.question[:50] + '...' if len(obj.question) > 50 else obj.question
    question_preview.short_description = 'Question'
