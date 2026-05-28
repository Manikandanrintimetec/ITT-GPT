
# Advanced RAG Chat API

Advanced RAG Chat API is a production-grade conversational AI backend built with FastAPI that combines multi-provider Large Language Models (LLMs) with Retrieval-Augmented Generation (RAG) for context-aware document-based conversations.

The application allows users to upload PDF documents, automatically processes and embeds them using sentence-transformers, and stores vector embeddings in ChromaDB for semantic retrieval. During chat interactions, the system retrieves the most relevant document chunks and injects them into the LLM prompt to generate accurate and contextual responses.

---

## Features

* Multi-Provider LLM Support

  * OpenRouter
  * Azure OpenAI
  * HuggingFace
  * Ollama

* Retrieval-Augmented Generation (RAG)

* PDF Upload, Chunking & Embedding

* ChromaDB Vector Storage

* Hybrid Semantic + BM25 Retrieval

* Query Rewriting for Conversational Search

* JWT Authentication & Authorization

* PostgreSQL Persistence

* Structured Logging with Loguru

* Rate Limiting Middleware

* Swagger UI & ReDoc Documentation

* Modular & Scalable Architecture

---

## Technology Stack

| Component       | Technology / Library   |
| --------------- | ---------------------- |
| Web Framework   | FastAPI                |
| ASGI Server     | Uvicorn                |
| Database        | PostgreSQL             |
| ORM             | SQLAlchemy             |
| Vector Database | ChromaDB               |
| Embeddings      | sentence-transformers  |
| RAG Framework   | LangChain              |
| Authentication  | JWT                    |
| Logging         | Loguru                 |
| Testing         | pytest + httpx         |
| NLP Libraries   | spaCy, NLTK, rank-bm25 |

---

## Architecture Overview

The application follows a layered architecture:

```text
Client Layer
     ↓
API Layer
     ↓
Router Layer
     ↓
Service Layer
     ↓
Data & Vector Layer
```

### Request Flow

1. Client sends chat request
2. Middleware validates request & rate limits
3. Router authenticates user
4. RAG retriever fetches relevant context
5. LLM provider generates response
6. Conversation data stored in PostgreSQL
7. JSON response returned

---

## Project Structure

```text
app/
├── main.py
├── core/
├── models/
├── routers/
├── schemas/
├── services/
├── llm/
├── rag/
├── utils/
└── tests/
```

---

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/Manikandanrintimetec/ITT-GPT.git
cd ITT-GPT
```

---

### 2. Create Virtual Environment

```bash
python -m venv .venv
```

### Activate Environment

#### Windows

```bash
.venv\Scripts\activate
```

#### Linux / Mac

```bash
source .venv/bin/activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file in the root directory.

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/itt_gpt

LLM_PROVIDER=openrouter

OPENROUTER_API_KEY=your_api_key

HUGGINGFACE_API_KEY=your_hf_key

HF_MODEL=mistralai/Mistral-7B-Instruct-v0.1

OLLAMA_MODEL=llama3
OLLAMA_BASE_URL=http://localhost:11434
```

---

## Running the Application

### Development Server

```bash
uvicorn app.main:app --reload
```

### Production Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## API Documentation

| Documentation | URL                         |
| ------------- | --------------------------- |
| Swagger UI    | http://localhost:8000/docs  |
| ReDoc         | http://localhost:8000/redoc |

---

## Core Functionalities

### PDF RAG Pipeline

* Upload PDF documents
* Split text into chunks
* Generate embeddings
* Store vectors in ChromaDB
* Retrieve relevant context during chat

### Multi-Provider LLM System

The system dynamically switches between providers using environment variables.

Supported providers:

* OpenRouter
* Azure OpenAI
* HuggingFace
* Ollama

### Hybrid Retrieval

Retrieval combines:

* Semantic similarity search
* BM25 keyword ranking
* Query rewriting

---

## Security Features

* JWT Authentication
* bcrypt Password Hashing
* Request Rate Limiting
* Exception Handling
* Structured Logging

---

## Running Tests

```bash
pytest -v
```

---

## Future Improvements

* Redis-based distributed rate limiting
* Streaming chat responses
* Multi-document retrieval
* Pinecone / Qdrant integration
* Conversation summarization
* Docker & Kubernetes deployment

---

## License

This project is intended for educational, research, and internal development purposes.
