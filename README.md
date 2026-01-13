# Knowledge Assistant API - RAG System

A Django-based backend system that powers a Knowledge Assistant API using Retrieval-Augmented Generation (RAG) to answer questions based on uploaded documents.

## 🚀 Features

- **Document Ingestion**: Upload and process PDFs, Markdown, and text files
- **RAG-Based Querying**: Retrieval-Augmented Generation to reduce hallucinations
- **Vector Search**: FAISS-powered semantic search across documents
- **LLM Integration**: OpenAI GPT integration with prompt engineering
- **Caching Layer**: Redis-based caching for frequent queries
- **REST API**: Clean Django REST Framework endpoints

## 📋 Tech Stack

- **Backend**: Django 5.0 + Django REST Framework
- **LLM**: OpenAI GPT-3.5/4 or HuggingFace Transformers
- **Vector DB**: FAISS with Sentence Transformers
- **Document Parsing**: PyPDF2, pdfplumber, python-docx
- **Caching**: Redis
- **Embeddings**: OpenAI text-embedding-ada-002

## 🛠️ Installation

1. **Clone the repository**
```bash
cd KnowledgeAssistant-RAG
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your API keys and settings
```

5. **Run migrations**
```bash
python manage.py migrate
python manage.py createsuperuser
```

6. **Start the server**
```bash
python manage.py runserver
```

## 📚 API Endpoints

### 1. Upload Documents
```http
POST /api/documents/upload/
Content-Type: multipart/form-data

{
  "file": <PDF/Markdown/Text file>,
  "title": "Science Class IX",
  "description": "NCERT Science textbook"
}
```

### 2. Ask Questions
```http
POST /api/ask-question/
Content-Type: application/json

{
  "question": "What is the use of mitochondria?"
}

Response:
{
  "answer": "The mitochondria is known as the powerhouse of the cell...",
  "sources": ["Science_Class_IX.pdf - Page 3"],
  "confidence": 0.92
}
```

### 3. List Documents
```http
GET /api/documents/
```

### 4. Delete Document
```http
DELETE /api/documents/{id}/
```

## 🔧 Configuration

Edit `.env` file:
- `OPENAI_API_KEY`: Your OpenAI API key
- `CHUNK_SIZE`: Text chunk size for embeddings (default: 500)
- `MAX_RETRIEVED_CHUNKS`: Number of chunks to retrieve for context (default: 5)

## 🧪 Testing

```bash
python manage.py test
```

## 📖 How It Works

1. **Document Upload**: Files are parsed and split into semantic chunks
2. **Embedding Generation**: Each chunk is converted to vector embeddings
3. **Vector Storage**: Embeddings stored in FAISS index
4. **Query Processing**: User question is embedded and similar chunks retrieved
5. **RAG Generation**: Retrieved context + question sent to LLM
6. **Response**: Optimized answer with source attribution

## 🎯 Roadmap

- [ ] Support for more file formats (DOCX, HTML)
- [ ] Multi-language support
- [ ] Query history and analytics
- [ ] Advanced chunking strategies
- [ ] Fine-tuned embedding models

## 📝 License

MIT License
