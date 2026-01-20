# Theological Conversational Agent 🛡️📖

A RAG (Retrieval-Augmented Generation) based AI assistant designed to answer theological and biblical questions with accuracy and pastoral tone.

## ✨ Features
- **Pastoral Persona**: The AI acts as a "Wise Christian Master," providing answers that are empathetic, pedagogical, and spiritually focused.
- **Contextual Memory**: Can answer follow-up questions contextually (e.g., "Who was he?" refers back to the previous subject).
- **Streaming Responses**: Real-time typing effect for a fluid conversational experience.
- **Multi-Source Knowledge**:
    - **Structured Bible**: Semantic chunking preserving context (Book/Chapter/Verse).
    - **Theological Library**: Supports PDF, Markdown, and **EPUB** ingestion.
    - **Duplicate Protection**: Intelligent ingestion system that prevents duplicate data entry.
- **Transparent Sourcing**: Every answer provides the list of documents/verses used for the response.

## 🏗️ Architecture
- **Backend**: Python (FastAPI) + LangChain
- **LLM**: Google Gemini (`gemini-1.5-flash` or similar)
- **Embeddings**: Google (`models/text-embedding-004`)
- **Vector DB**: ChromaDB (Docker)
- **Frontend**: Flutter (Mobile/Web) with a "Parchment & Burgundy" theme.

## 🚀 Getting Started

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [Flutter SDK](https://flutter.dev/docs/get-started/install)
- [Google Gemini API Key](https://aistudio.google.com/)

### 1. Setup Environment
Clone the repository and set up your variables:
```bash
cp .env.example .env
# Open .env and add your GOOGLE_API_KEY
```

### 2. Run Backend
Start the API and Database using Docker:
```bash
docker-compose up --build -d
```
The API becomes available at `http://localhost:8001`.

### 3. Ingest Data (Expand Knowledge)
Load your theological documents into the vector database.
Supported formats: **PDF**, **EPUB**, **Markdown**, **JSON (Bible Structure)**.

1. Place files in `source_docs/`.
2. Run the helper script:
```bash
./scripts/refresh_knowledge.sh
```
Or manually via Docker:
```bash
docker-compose exec backend python data_ingestion/ingest.py
```
*Note: The ingestor automatically checks for existing files to avoid duplicates.*

### 4. Run Frontend
Launch the mobile/web application:
```bash
cd frontend
flutter pub get
flutter run
```

## 🛠️ Verification
- **Backend Test**: `curl -X POST "http://localhost:8001/chat" -d '{"query": "Quem foi Paulo?"}'`
- **Frontend**: Built with Flutter 3.x, tested on Android & Web.

## 📄 License
[MIT](LICENSE)