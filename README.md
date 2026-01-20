# Scripture AI Assistant 🛡️📖
> **MBA USP/Esalq - TCC Project**
> *Agente Teológico Conversacional com Arquitetura RAG e Reranking Semântico*

Este projeto implementa um **Assistente Teológico Inteligente** capaz de responder dúvidas doutrinárias e bíblicas com alta precisão, fidelidade teológica e tom pastoral ("Persona"). Diferente de chats genéricos, ele opera sob o princípio *Sola Scriptura*, utilizando apenas documentos verificados (Bíblia, Teologia Sistemática) como fonte de verdade.

## ✨ Diferenciais Acadêmicos
*   **🧠 RAG com Reranking**: Utiliza **FlashRank** para refinar a busca vetorial (ChromaDB), garantindo que apenas os trechos semanticamente mais relevantes sejam enviados ao modelo (Precision@K otimizado).
*   **📊 Avaliação Quantitativa**: Validado pelo framework **RAGAS** (Retrieval Augmented Generation Assessment), medindo métricas como *Answer Relevancy* e *Context Precision*.
*   **🔗 Citações Interativas**: Frontend Flutter com sistema de "Deep Linking" para referências bíblicas. Clicar em `[Gênesis 1:1]` abre o texto original instantaneamente.
*   **🐳 100% Dockerized**: Backend (Python/FastAPI) e Frontend (Flutter Web/Nginx) totalmente containerizados para fácil reprodução.

## 🏗️ Arquitetura Técnica

```mermaid
graph LR
    User[Usuário (Flutter/Web)] -->|HTTPS| Nginx[Nginx Proxy :3000]
    Nginx -->|/api| API[FastAPI Backend :8000]
    API -->|Prompt| Reform[LLM: Reformulação]
    Reform -->|Query| Vector[ChromaDB (Busca Híbrida)]
    Vector -->|Docs Brutos (Top 20)| Reranker[FlashRank (ms-marco-Minilm)]
    Reranker -->|Docs Refinados (Top 6)| LLM[Google Gemini 1.5 Flash]
    LLM -->|Resposta Pastoral| Streaming[SSE Stream]
    Streaming --> User
```

## 🚀 Como Executar (Plug & Play)

Pré-requisitos: [Docker Desktop](https://www.docker.com/products/docker-desktop) instalado e uma chave de API do [Google AI Studio](https://aistudio.google.com/).

### 1. Configuração
Clone o repositório e configure sua chave:
```bash
cp .env.example .env
# Edite o arquivo .env e cole sua GOOGLE_API_KEY
```

### 2. Rodar Aplicação
Basta um único comando para subir toda a infraestrutura (Banco, Backend e Frontend):
```bash
docker-compose up --build
```
*   **Frontend**: Acesse `http://localhost:3000` 🌐
*   **Backend API**: Disponível em `http://localhost:8001/docs` ⚙️

### 3. Ingestão de Conhecimento
Para alimentar a "mente" do agente com novos PDFs, EPUBs ou Markdown:
1.  Coloque os arquivos na pasta `source_docs/`.
2.  Execute o script de ingestão:
    ```bash
    ./scripts/refresh_knowledge.sh
    # Ou via Docker: docker-compose exec backend python data_ingestion/ingest.py
    ```

## 📊 Avaliação de Performance
O projeto inclui um pipeline de avaliação automatizado (`evaluation/`).

| Métrica | Resultado (Média) | Descrição |
| :--- | :--- | :--- |
| **Answer Relevancy** | **0.75** | Alta aderência à pergunta do usuário. |
| **Latência Média** | **~2.5s** | Tempo para o primeiro token (TTFT). |

Para reproduzir os testes:
```bash
docker-compose exec backend python evaluation/run_eval.py
```
Isso gerará novos gráficos em `evaluation/charts/`.

## 🛠️ Stack Tecnológica
*   **LLM**: Google Gemini 1.5 Flash
*   **Vector Store**: ChromaDB
*   **Reranker**: FlashRank (On-CPU)
*   **Backend**: Python 3.12, FastAPI, LangChain
*   **Frontend**: Flutter 3.x (Web & Mobile)
*   **Infra**: Docker Compose

## 📄 Licença
Projeto acadêmico desenvolvido para fins de pesquisa e conclusão de curso (MBA Data Science & Analytics - USP/Esalq).