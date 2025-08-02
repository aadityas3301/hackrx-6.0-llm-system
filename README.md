# 🚀 HackRx 6.0 - LLM Document Query System

Simple and efficient document processing system with LLM-powered question answering for insurance policies and legal documents.

## ✨ What it does

- Processes PDF documents from URLs
- Answers questions about document content using AI
- Returns structured JSON responses
- Handles multiple questions at once

## 🛠️ Tech Stack

- **FastAPI** - Web API
- **OpenAI GPT-4** - Language model
- **Scikit-learn** - Vector search
- **PyPDF2** - PDF processing

##  Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment:**
   Create `.env` file:
   ```
   OPENAI_API_KEY=your_openai_key_here
   ```

3. **Run the server:**
   ```bash
   python main.py
   ```
   Server runs on: `http://localhost:8080`

## 📡 API Usage

**Endpoint:** `POST /hackrx/run`

**Headers:**
```
Authorization: Bearer 667efb9a18a1e0cb1dbc77a25fddc98c12849e980fc25cc9dea06eca61b1f4c8
Content-Type: application/json
```

**Request:**
```json
{
  "documents": "https://example.com/policy.pdf",
  "questions": [
    "What is the grace period?",
    "What are the benefits?"
  ]
}
```

**Response:**
```json
{
  "answers": [
    "Grace period is 30 days...",
    "Benefits include medical coverage..."
  ]
}
```

## 🌐 Deployment

**Railway:**
1. Connect GitHub repo to Railway
2. Add `OPENAI_API_KEY` in environment variables
3. Deploy

**Heroku:**
```bash
heroku create your-app
heroku config:set OPENAI_API_KEY=your_key
git push heroku main
```

## 🧪 Test the System

```bash
python production_test.py
```
This runs comprehensive tests and shows accuracy scores.

## 📁 Project Structure

```
├── main.py                          # Main API server
├── enhanced_llm_processor.py         # AI processing
├── advanced_document_processor.py    # Document handling
├── vector_database.py              # Search engine
├── production_test.py              # Testing suite
└── requirements.txt                # Dependencies
```

---

**Built for HackRx 6.0** 🏆 