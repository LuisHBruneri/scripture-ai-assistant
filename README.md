# Scripture AI Assistant 🛡️📖
>
> **MBA USP/Esalq - TCC Project**
> *Agente Teológico Conversacional com Arquitetura RAG e Reranking Semântico*

Este projeto implementa um **Assistente Teológico Inteligente** capaz de responder dúvidas doutrinárias e bíblicas com alta precisão, fidelidade teológica e tom pastoral ("Persona"). Diferente de chats genéricos, ele opera sob o princípio *Sola Scriptura*, utilizando apenas documentos verificados (Bíblia, Teologia Sistemática) como fonte de verdade.

## ✨ Diferenciais Acadêmicos

* **🧠 RAG com Reranking**: Utiliza **FlashRank** para refinar a busca vetorial (ChromaDB), garantindo que apenas os trechos semanticamente mais relevantes sejam enviados ao modelo (Precision@K otimizado).
* **📊 Avaliação Quantitativa**: Validado pelo framework **RAGAS** (Retrieval Augmented Generation Assessment), medindo métricas como *Answer Relevancy* e *Context Precision*.
* **🔗 Citações Interativas**: Frontend Flutter com sistema de "Deep Linking" para referências bíblicas. Clicar em `[Gênesis 1:1]` abre o texto original instantaneamente.
* **🐳 100% Dockerized**: Backend (Python/FastAPI) e Frontend (Flutter Web/Nginx) totalmente containerizados para fácil reprodução.

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
# Edite o arquivo .env e cole sua GOOGLE_API_KEY e GOOGLE_MODEL_NAME (DEFAULT: gemini-2.5-flash-lite)
```

### 2. Rodar Aplicação (Modo Fácil)

Utilize os scripts facilitadores para gerenciar o projeto sem decorar comandos Docker:

```bash
# Iniciar tudo (Backend + Frontend + Banco)
./scripts/start_app.sh

# Ver logs em tempo real
./scripts/view_logs.sh

# Parar aplicação
./scripts/stop_app.sh
```

* **Frontend**: Acesse `http://localhost:3000` 🌐
* **Backend API**: Disponível em `http://localhost:8001/docs` ⚙️

### 3. Ingestão de Conhecimento Automatizada

Para alimentar a "mente" do agente com a Bíblia e recursos teológicos:

1. **Modo Automático**:
    Execute o script mestre que baixa a Bíblia e processa tudo:

    ```bash
    ./scripts/train.sh
    ```

    *Isso executará o download de recursos, a limpeza inteligente de PDFs e a ingestão no ChromaDB.*

2. **Modo Manual**:
    Coloque seus arquivos (PDF, EPUB, TXT) em `source_docs/` e rode o `./scripts/train.sh` novamente.

> **Importante**: Consulte `AGENT_RULES.md` para regras estritas de desenvolvimento e teologia.

## 📊 Validação Científica (Nível MBA)

O projeto inclui um pipeline rigoroso de testes para validação acadêmica, com suporte a **Estudos Comparativos (A/B)** e **Ablação**.

### 🧪 Modos de Teste

| Modo | Comando | Objetivo |
| :--- | :--- | :--- |
| **Experimental** (Agente) | `./scripts/run_validation.sh` | Avaliar qualidade máxima (RAG + Rerank + Persona). |
| **Controle** (Baseline) | `./scripts/run_validation.sh --baseline` | Avaliar LLM puro para provar valor do RAG. |
| **Ablação** (No-Rerank) | `./scripts/run_validation.sh --no-rerank` | Provar a necessidade do FlashRank na arquitetura. |

### 🔬 Reprodução Completa ("One-Click Thesis")

Para reproduzir **todos** os experimentos da tese e gerar os relatórios comparativos automaticamente:

```bash
./scripts/run_full_experiment.sh
```

Isso gerará 3 artefatos em `evaluation/`:
1.  `agent_report.md`: Resultados do Sistema Proposto.
2.  `baseline_report.md`: Resultados da Linha de Base.
3.  `ablation_report.md`: Justificativa Arquitetural.
4.  `results.csv`: Dados brutos com latência e métricas RAGAS.

> **Nota**: O tempo total de execução é de aprox. 45-60 min devido aos Rate Limits do Gemini Free Tier.

## 🛠️ Stack Tecnológica

* **LLM**: Google Gemini (DEFAULT: gemini-2.5-flash-lite)
* **Vector Store**: ChromaDB
* **Reranker**: FlashRank (On-CPU)
* **Backend**: Python 3.12, FastAPI, LangChain
* **Frontend**: Flutter 3.x (Web & Mobile)
* **Infra**: Docker Compose

## 📄 Licença

Projeto acadêmico desenvolvido para fins de pesquisa e conclusão de curso (MBA Engenharia de Software - USP/Esalq).

---

Desenvolvido por [Luis Henrique Bruneri](https://github.com/luishbruneri) 🇧🇷
