# Theological Conversational Agent 🛡️📖

A RAG (Retrieval-Augmented Generation) based AI assistant designed to answer theological and biblical questions with accuracy and pastoral tone.

## 🏗️ Architecture
- **Backend**: Python (FastAPI) + LangChain
- **LLM**: Google Gemini (`gemini-3-flash-preview`)
- **Embeddings**: Google (`models/text-embedding-004`)
- **Vector DB**: ChromaDB (Docker)
- **Frontend**: Flutter (Mobile/Web)

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
Load your theological documents (PDFs/Markdown) into the vector database:
1. Place PDF or Markdown files in `source_docs/`.
2. Run the helper script:
```bash
./refresh_knowledge.sh
```
Alternatively, using Docker directly:
```bash
docker-compose exec backend python data_ingestion/ingest.py
```

### 4. Run Frontend
Launch the mobile/web application:
```bash
cd frontend
flutter pub get
flutter run
```

## 🛠️ Tech Stack Verification
- **Backend Test**: `curl -X POST "http://localhost:8001/chat" -d '{"query": "Hello"}'`
- **Frontend**: Built with Flutter 3.x, tested on Android & Web.

## 📄 License
[MIT](LICENSE)