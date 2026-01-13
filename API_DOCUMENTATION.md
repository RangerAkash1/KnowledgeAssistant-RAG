# Knowledge Assistant API - Postman Collection

## API Endpoints

### 1. Upload Document
```
POST http://localhost:8000/api/documents/upload/
Content-Type: multipart/form-data

Body (form-data):
- file: <select PDF/Markdown/Text file>
- title: "Science Class IX"
- description: "NCERT Science textbook for Class 9"
```

### 2. Ask Question
```
POST http://localhost:8000/api/ask-question/
Content-Type: application/json

Body:
{
    "question": "What is the use of mitochondria?",
    "max_chunks": 5,
    "temperature": 0.7
}
```

### 3. List All Documents
```
GET http://localhost:8000/api/documents/
```

### 4. Get Specific Document
```
GET http://localhost:8000/api/documents/{id}/
```

### 5. Delete Document
```
DELETE http://localhost:8000/api/documents/{id}/
```

### 6. Query History
```
GET http://localhost:8000/api/query-history/
```

### 7. System Statistics
```
GET http://localhost:8000/api/stats/
```

### 8. Clear Cache
```
POST http://localhost:8000/api/clear-cache/
```

## Sample Response - Ask Question

```json
{
    "answer": "The mitochondria is known as the powerhouse of the cell because it produces energy in the form of ATP (Adenosine Triphosphate) through cellular respiration. This energy is essential for various cellular processes and functions.",
    "sources": [
        "Science_Class_IX.pdf - Page 3",
        "Science_Class_IX.pdf - Page 5"
    ],
    "confidence": 0.89,
    "processing_time": 2.34,
    "cached": false
}
```

## Sample cURL Commands

### Upload Document
```bash
curl -X POST http://localhost:8000/api/documents/upload/ \
  -F "file=@/path/to/document.pdf" \
  -F "title=Science Class IX" \
  -F "description=NCERT Science textbook"
```

### Ask Question
```bash
curl -X POST http://localhost:8000/api/ask-question/ \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the use of mitochondria?"
  }'
```
