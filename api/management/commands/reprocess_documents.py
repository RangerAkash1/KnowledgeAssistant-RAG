"""
Management command to process existing documents
"""
from django.core.management.base import BaseCommand
from api.models import Document
from api.views import DocumentProcessor, TextChunker, vector_db
from django.conf import settings


class Command(BaseCommand):
    help = 'Reprocess all documents and rebuild vector database'
    
    def handle(self, *args, **options):
        self.stdout.write('Starting document reprocessing...')
        
        documents = Document.objects.filter(status='completed')
        
        for doc in documents:
            self.stdout.write(f'Processing: {doc.title}')
            
            try:
                # Clear existing chunks
                doc.chunks.all().delete()
                
                # Process document
                processor = DocumentProcessor()
                pages_content = processor.process_document(doc.file.path, doc.file_type)
                
                # Chunk text
                chunker = TextChunker(
                    chunk_size=settings.CHUNK_SIZE,
                    chunk_overlap=settings.CHUNK_OVERLAP
                )
                chunks = chunker.chunk_document(pages_content)
                
                # Save chunks
                from api.models import DocumentChunk
                chunk_objects = []
                for chunk_data in chunks:
                    chunk_obj = DocumentChunk.objects.create(
                        document=doc,
                        content=chunk_data['content'],
                        chunk_index=chunk_data['chunk_index'],
                        page_number=chunk_data['page_number']
                    )
                    chunk_objects.append(chunk_obj)
                
                doc.num_chunks = len(chunks)
                doc.save()
                
                self.stdout.write(self.style.SUCCESS(f'✓ Processed {doc.title}'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Failed: {doc.title} - {str(e)}'))
        
        # Rebuild vector database
        self.stdout.write('Rebuilding vector database...')
        vector_db.rebuild_index()
        
        self.stdout.write(self.style.SUCCESS('Done!'))
