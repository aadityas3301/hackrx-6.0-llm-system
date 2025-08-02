# 🚀 HackRx 6.0 - Intelligent Query Retrieval System

A winning solution for the HackRx 6.0 hackathon featuring an LLM-powered intelligent query-retrieval system that processes large documents and makes contextual decisions for insurance, legal, HR, and compliance domains.

## 🏆 Features

- **Multi-Format Document Processing**: PDF, DOCX, HTML/Email support
- **Semantic Search**: Advanced vector embeddings with Pinecone
- **Intelligent Query Processing**: GPT-4 powered context-aware responses
- **Explainable Decisions**: Clear reasoning and clause traceability
- **High Performance**: Optimized for speed and accuracy
- **Scalable Architecture**: Modular design for easy extension

## 🛠️ Tech Stack

- **Backend**: FastAPI
- **Vector Database**: Pinecone (with in-memory fallback)
- **LLM**: OpenAI GPT-4
- **Embeddings**: Sentence Transformers
- **Document Processing**: PyPDF2, python-docx
- **Deployment**: Ready for Heroku, Vercel, Railway, AWS, etc.

## 📋 Prerequisites

- Python 3.8+
- OpenAI API Key
- Pinecone API Key (optional - falls back to in-memory)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <your-repo>
cd Bajaj_LLM
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file based on `env_example.txt`:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Pinecone Configuration (Optional)
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=gcp-starter

# API Configuration
API_TOKEN=667efb9a18a1e0cb1dbc77a25fddc98c12849e980fc25cc9dea06eca61b1f4c8
```

### 3. Run Locally

```bash
python main.py
```

The API will be available at `http://localhost:8000`

### 4. Test the API

```bash
curl -X POST "http://localhost:8000/hackrx/run" \
  -H "Authorization: Bearer 667efb9a18a1e0cb1dbc77a25fddc98c12849e980fc25cc9dea06eca61b1f4c8" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
    "questions": [
      "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
      "What is the waiting period for pre-existing diseases (PED) to be covered?"
    ]
  }'
```

## 🌐 Deployment

### Heroku Deployment

1. Create `Procfile`:
```
web: uvicorn main:app --host=0.0.0.0 --port=$PORT
```

2. Deploy:
```bash
heroku create your-app-name
heroku config:set OPENAI_API_KEY=your_key
heroku config:set PINECONE_API_KEY=your_key
git push heroku main
```

### Railway Deployment

1. Connect your GitHub repo to Railway
2. Set environment variables in Railway dashboard
3. Deploy automatically

### Vercel Deployment

1. Create `vercel.json`:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "main.py"
    }
  ]
}
```

2. Deploy:
```bash
vercel --prod
```

## 📊 API Endpoints

### Main Endpoint
- **POST** `/hackrx/run` - Process document queries
- **POST** `/api/v1/hackrx/run` - Alternative endpoint

### Health & Info
- **GET** `/` - API information
- **GET** `/health` - Health check

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `PINECONE_API_KEY` | Pinecone API key | Optional |
| `PINECONE_ENVIRONMENT` | Pinecone environment | `gcp-starter` |
| `CHUNK_SIZE` | Document chunk size | `1000` |
| `CHUNK_OVERLAP` | Chunk overlap | `200` |
| `TOP_K_RESULTS` | Search results count | `5` |

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Document      │    │   Vector        │    │   LLM           │
│   Processor     │───▶│   Store         │───▶│   Processor     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PDF/DOCX      │    │   Pinecone      │    │   GPT-4         │
│   Processing    │    │   Embeddings    │    │   Generation    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🎯 Evaluation Criteria

Our solution is optimized for all evaluation parameters:

- **Accuracy**: High-precision semantic search with context-aware responses
- **Token Efficiency**: Optimized chunking and prompt engineering
- **Latency**: Fast vector search and efficient processing
- **Reusability**: Modular architecture with clear separation of concerns
- **Explainability**: Detailed reasoning and source attribution

## 🧪 Testing

### Local Testing

```bash
# Test with sample data
python -c "
import requests
import json

url = 'http://localhost:8000/hackrx/run'
headers = {
    'Authorization': 'Bearer 667efb9a18a1e0cb1dbc77a25fddc98c12849e980fc25cc9dea06eca61b1f4c8',
    'Content-Type': 'application/json'
}
data = {
    'documents': 'https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D',
    'questions': ['What is the grace period for premium payment?']
}

response = requests.post(url, headers=headers, json=data)
print(json.dumps(response.json(), indent=2))
"
```

## 📈 Performance Optimization

- **Chunking Strategy**: Optimal chunk size with overlap for context preservation
- **Vector Search**: Efficient similarity search with configurable thresholds
- **Caching**: In-memory caching for repeated queries
- **Async Processing**: Non-blocking operations for better throughput

## 🔒 Security

- Bearer token authentication
- Input validation and sanitization
- Rate limiting ready
- Secure API key handling

## 📝 License

This project is created for HackRx 6.0 hackathon.

## 🤝 Contributing

This is a hackathon project, but contributions are welcome!

## 📞 Support

For hackathon-related questions, please refer to the official HackRx 6.0 documentation.

---

**Good luck with the hackathon! 🚀** 