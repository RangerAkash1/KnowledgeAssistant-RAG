# Quick Start Guide

## Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)
- OpenAI API key (or use local embeddings)

## Installation

### Windows
```bash
# Run the setup script
setup.bat

# Or manually:
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# Edit .env with your settings
python manage.py migrate
python manage.py createsuperuser
```

### Linux/Mac
```bash
# Run the setup script
chmod +x setup.sh
./setup.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your settings
python manage.py migrate
python manage.py createsuperuser
```

## Configuration

1. **Edit .env file** with your settings:
   ```
   OPENAI_API_KEY=sk-your-api-key-here
   OPENAI_MODEL=gpt-3.5-turbo
   CHUNK_SIZE=500
   MAX_RETRIEVED_CHUNKS=5
   ```

2. **Create superuser** for admin access:
   ```bash
   python manage.py createsuperuser
   ```

## Running the Server

```bash
# Activate virtual environment (if not already active)
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Run development server
python manage.py runserver

# Server will be available at http://localhost:8000
```

## Testing the API

### 1. Upload a Document

Using cURL:
```bash
curl -X POST http://localhost:8000/api/documents/upload/ \
  -F "file=@sample_data/science_class_ix.md" \
  -F "title=Science Class IX" \
  -F "description=Sample science document"
```

Using Python:
```python
import requests

url = "http://localhost:8000/api/documents/upload/"
files = {'file': open('sample_data/science_class_ix.md', 'rb')}
data = {
    'title': 'Science Class IX',
    'description': 'Sample science document'
}

response = requests.post(url, files=files, data=data)
print(response.json())
```

### 2. Ask a Question

Using cURL:
```bash
curl -X POST http://localhost:8000/api/ask-question/ \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the use of mitochondria?"}'
```

Using Python:
```python
import requests

url = "http://localhost:8000/api/ask-question/"
data = {"question": "What is the use of mitochondria?"}

response = requests.post(url, json=data)
print(response.json())
```

### 3. Access Admin Panel

Visit: http://localhost:8000/admin/
Login with your superuser credentials

## Features to Test

1. **Document Upload**: Upload PDF, Markdown, or Text files
2. **Question Answering**: Ask questions about uploaded documents
3. **Source Attribution**: See which documents and pages were used
4. **Caching**: Repeated queries are cached for faster responses
5. **Query History**: View all past queries in admin panel
6. **Statistics**: Check system stats at `/api/stats/`

## Troubleshooting

### Issue: OpenAI API errors
**Solution**: Check your API key in `.env` file or set `use_openai=False` in `vector_db.py`

### Issue: Module not found errors
**Solution**: 
```bash
pip install -r requirements.txt --force-reinstall
```

### Issue: Database errors
**Solution**:
```bash
python manage.py migrate --run-syncdb
```

### Issue: Vector database not loading
**Solution**:
```bash
# Clear and rebuild
python manage.py shell
>>> from api.utils.vector_db import vector_db
>>> vector_db.clear()
>>> exit()

# Reprocess documents
python manage.py reprocess_documents
```

## Performance Tips

1. **Use Redis for caching** (production):
   - Uncomment Redis settings in `settings.py`
   - Install Redis: `pip install django-redis redis`
   - Start Redis server

2. **Batch document uploads**:
   - Upload multiple documents at once for better efficiency

3. **Tune chunk size**:
   - Adjust `CHUNK_SIZE` in `.env` based on your documents
   - Smaller chunks: More precise but more API calls
   - Larger chunks: More context but less precise

4. **Use local embeddings**:
   - If OpenAI is slow/expensive, use sentence-transformers
   - Edit `vector_db.py` to set `use_openai=False`

## Next Steps

1. Integrate with frontend (React, Next.js, etc.)
2. Add authentication and user management
3. Deploy to production (Heroku, AWS, Azure)
4. Add more document formats (DOCX, HTML)
5. Implement advanced RAG techniques
6. Add multilingual support

## Support

For issues or questions:
- Check the documentation in `README.md`
- Review API docs in `API_DOCUMENTATION.md`
- Check Django logs for errors
