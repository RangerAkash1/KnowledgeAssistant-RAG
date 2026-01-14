# Knowledge Assistant - Complete API Documentation

## Base URL
```
http://localhost:8000/api/
```

## Authentication
All endpoints require token-based authentication via the `Authorization` header:
```
Authorization: Token changeme-token
```

---

## 1. UPLOAD DOCUMENT

### Endpoint
```
POST /documents/upload/
```

### Description
Upload and process a document (PDF, Markdown, or Text file) to the knowledge base.

### Request
**Content-Type:** `multipart/form-data`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | file | Yes | Document file (PDF, .md, .txt) |
| `title` | string | Yes | Document title |
| `description` | string | No | Document description |

### Example cURL
```bash
curl -X POST http://localhost:8000/api/documents/upload/ \
  -H "Authorization: Token changeme-token" \
  -F "file=@sample_data/science_class_ix.md" \
  -F "title=Science Class IX" \
  -F "description=NCERT Science textbook for Class 9"
```

### Response (200 OK)
```json
{
  "message": "Document uploaded and processed successfully",
  "document": {
    "id": 4,
    "title": "Science Class IX",
    "description": "NCERT Science textbook for Class 9",
    "file": "/media/documents/science_class_ix_8cjen9O.md",
    "file_type": "md",
    "file_size": 1897,
    "status": "completed",
    "num_chunks": 5,
    "uploaded_at": "2026-01-13T18:38:55.975302Z",
    "processed_at": "2026-01-13T18:38:56.123456Z"
  }
}
```

### Error Response (400 Bad Request)
```json
{
  "file": ["No file was submitted."],
  "title": ["This field is required."]
}
```

---

## 2. LIST ALL DOCUMENTS

### Endpoint
```
GET /documents/
```

### Description
Retrieve a list of all uploaded documents in the knowledge base.

### Parameters
None

### Example cURL
```bash
curl -X GET http://localhost:8000/api/documents/ \
  -H "Authorization: Token changeme-token"
```

### Response (200 OK)
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 4,
      "title": "Science Class IX",
      "description": "NCERT Science textbook for Class 9",
      "file_type": "md",
      "file_size": 1897,
      "status": "completed",
      "num_chunks": 5,
      "uploaded_at": "2026-01-13T18:38:55.975302Z"
    },
    {
      "id": 5,
      "title": "Biology Basics",
      "description": "Biology fundamentals",
      "file_type": "txt",
      "file_size": 2500,
      "status": "completed",
      "num_chunks": 8,
      "uploaded_at": "2026-01-13T19:10:20.123456Z"
    }
  ]
}
```

---

## 3. GET SPECIFIC DOCUMENT

### Endpoint
```
GET /documents/{id}/
```

### Description
Retrieve details of a specific document by ID.

### Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | integer | Yes | Document ID |

### Example cURL
```bash
curl -X GET http://localhost:8000/api/documents/4/ \
  -H "Authorization: Token changeme-token"
```

### Response (200 OK)
```json
{
  "id": 4,
  "title": "Science Class IX",
  "description": "NCERT Science textbook for Class 9",
  "file": "/media/documents/science_class_ix_8cjen9O.md",
  "file_type": "md",
  "file_size": 1897,
  "status": "completed",
  "num_chunks": 5,
  "uploaded_at": "2026-01-13T18:38:55.975302Z",
  "processed_at": "2026-01-13T18:38:56.123456Z"
}
```

### Error Response (404 Not Found)
```json
{
  "detail": "Not found."
}
```

---

## 4. DELETE DOCUMENT

### Endpoint
```
DELETE /documents/{id}/
```

### Description
Delete a document and all its associated chunks from the knowledge base.

### Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | integer | Yes | Document ID |

### Example cURL
```bash
curl -X DELETE http://localhost:8000/api/documents/4/ \
  -H "Authorization: Token changeme-token"
```

### Response (204 No Content)
```
(Empty response)
```

---

## 5. ASK QUESTION

### Endpoint
```
POST /ask-question/
```

### Description
Ask a question about the documents in the knowledge base. Uses RAG to retrieve relevant context and generate an answer.

### Request
**Content-Type:** `application/json`

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `question` | string | Yes | - | The question to ask |
| `max_chunks` | integer | No | 5 | Max relevant chunks to retrieve |
| `temperature` | float | No | 0.7 | LLM temperature (0-1) |

### Example cURL
```bash
curl -X POST http://localhost:8000/api/ask-question/ \
  -H "Authorization: Token changeme-token" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is mitochondria and what is its main function?"
  }'
```

### Response (200 OK)
```json
{
  "answer": "Mitochondria is known as the powerhouse of the cell because it produces energy in the form of ATP (Adenosine Triphosphate) through cellular respiration. This energy is essential for various cellular processes and functions.",
  "sources": [
    {
      "document_id": 4,
      "document_title": "Science Class IX",
      "chunk_id": 2,
      "snippet": "Mitochondria is an organelle found in the cytoplasm of eukaryotic cells..."
    }
  ],
  "confidence": 0.89,
  "processing_time": 2.34,
  "cached": false,
  "timestamp": "2026-01-13T18:40:12.345678Z"
}
```

### Error Response (400 Bad Request)
```json
{
  "error": "No documents uploaded yet. Please upload documents first."
}
```

---

## 6. QUERY HISTORY

### Endpoint
```
GET /query-history/
```

### Description
Retrieve all previous queries and their answers.

### Parameters
None

### Example cURL
```bash
curl -X GET http://localhost:8000/api/query-history/ \
  -H "Authorization: Token changeme-token"
```

### Response (200 OK)
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "question": "What is mitochondria?",
      "answer": "Mitochondria is the powerhouse of the cell...",
      "sources_used": [4, 5],
      "cached": false,
      "processing_time": 2.34,
      "created_at": "2026-01-13T18:40:12.345678Z"
    },
    {
      "id": 2,
      "question": "What is mitochondria?",
      "answer": "Mitochondria is the powerhouse of the cell...",
      "sources_used": [4, 5],
      "cached": true,
      "processing_time": 0.02,
      "created_at": "2026-01-13T18:42:05.123456Z"
    }
  ]
}
```

---

## 7. SYSTEM STATISTICS

### Endpoint
```
GET /stats/
```

### Description
Get system statistics including document count, chunk count, total queries, and cache hit ratio.

### Parameters
None

### Example cURL
```bash
curl -X GET http://localhost:8000/api/stats/ \
  -H "Authorization: Token changeme-token"
```

### Response (200 OK)
```json
{
  "total_documents": 2,
  "total_chunks": 13,
  "total_queries": 5,
  "cache_hits": 1,
  "cache_miss": 4,
  "cache_hit_ratio": 0.2,
  "average_processing_time": 1.87,
  "vector_store_size": "2.3 MB"
}
```

---

## 8. CLEAR CACHE

### Endpoint
```
POST /clear-cache/
```

### Description
Clear all cached query results to free up memory.

### Parameters
None

### Example cURL
```bash
curl -X POST http://localhost:8000/api/clear-cache/ \
  -H "Authorization: Token changeme-token"
```

### Response (200 OK)
```json
{
  "message": "Cache cleared successfully",
  "cleared_entries": 15
}
```

---

## ERROR RESPONSES

### 401 Unauthorized
```json
{
  "detail": "Unauthorized"
}
```
**Cause:** Missing or invalid Authorization token

### 404 Not Found
```json
{
  "detail": "Not found."
}
```
**Cause:** Resource with given ID doesn't exist

### 400 Bad Request
```json
{
  "error": "Invalid request parameters"
}
```
**Cause:** Missing required fields or invalid data

### 500 Internal Server Error
```json
{
  "detail": "Internal Server Error"
}
```
**Cause:** Server error during processing

---

## RATE LIMITING & QUOTAS

- **File Size Limit**: 50 MB per document
- **Chunk Size**: Configurable (default: 500 characters)
- **Max Chunks Retrieved**: Configurable (default: 5)
- **Query Timeout**: 30 seconds

---

## QUICK START EXAMPLES

### Python
```python
import requests

headers = {"Authorization": "Token changeme-token"}

# Upload document
with open('sample.md', 'rb') as f:
    files = {'file': f}
    data = {'title': 'My Document', 'description': 'Test'}
    response = requests.post(
        'http://localhost:8000/api/documents/upload/',
        files=files,
        data=data,
        headers=headers
    )
    print(response.json())

# Ask question
response = requests.post(
    'http://localhost:8000/api/ask-question/',
    json={"question": "What is the main topic?"},
    headers=headers
)
print(response.json())
```

### JavaScript (Node.js)
```javascript
const token = "changeme-token";
const headers = {"Authorization": `Token ${token}`};

// Ask question
const response = await fetch('http://localhost:8000/api/ask-question/', {
  method: 'POST',
  headers: {
    ...headers,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    question: "What is the main topic?"
  })
});

const data = await response.json();
console.log(data);
```

---

## ADMIN PANEL

Access the Django admin panel to manage documents and queries:
```
http://localhost:8000/admin/
```

**Credentials**: Create with `python manage.py createsuperuser`

---

## SUPPORT & TROUBLESHOOTING

**Q: Getting "Unauthorized" error?**
A: Ensure you include the correct Authorization header with your API token.

**Q: File upload failing?**
A: Check file size (max 50 MB) and format (PDF, Markdown, TXT).

**Q: No answer from question endpoint?**
A: Ensure documents are uploaded and processed first.

**Q: Slow response times?**
A: Check cache hit ratio in `/stats/` and clear old queries if needed.

---

**API Version**: 1.0  
**Last Updated**: January 14, 2026  
**Framework**: Django REST Framework  
**Database**: SQLite with FAISS Vector Index
