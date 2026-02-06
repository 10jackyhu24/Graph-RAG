# Graph-RAG

A local-first GraphRAG pipeline for construction/manufacturing knowledge extraction.

## What It Does
- Layout-aware PDF parsing (tables + titles) using Unstructured (`hi_res`).
- IFC extraction (IfcOpenShell) to component summaries.
- Structured extraction via LangChain (`with_structured_output` or agent schema).
- Dual-track storage: Postgres (metadata + JSON), Chroma (semantic), Neo4j (graph).
- Multi-tenant isolation: Postgres schema + Chroma collection + Neo4j label per tenant.
- RAG chat with streaming responses (vector + documents + graph).
- Custom Agents: user-defined schema generation + versioning + deactivation.
- Meeting ASR (audio -> transcript -> extraction) with Whisper.
- Document management: list / download / delete.

## What Changed (Project History)
- Added **Agent builder**: user prompt -> JSON Schema -> structured extraction.
- Added **RAG chat** and **streaming** in the workspace UI.
- Added **document management**: list / download / delete + load previous results.
- Added **report tools**: PDF export + cute note generation.
- Added **ASR pipeline**: upload audio, Whisper transcribe, then extract.
- Added **multi-tenant isolation** across all three data stores.
- Added **embeddings provider switch**: Ollama or Sentence-Transformers.
- Added **DeepSeek API support**, keeping Ollama for local fallback.

## Quick Start (Local, New Developer)

### 1) Start Databases (Docker)
```
docker compose up -d
```

### 2) Backend Setup
```
cd backend
python -m venv .venv
.\.venv\Scripts\activate
```

Install dependencies:
```
.\.venv\Scripts\pip.exe install -r requirements.txt
```

Optional: ASR (Whisper) is already in `requirements.txt` but needs `ffmpeg` in PATH.

### 3) Frontend Setup
```
cd frontend
npm install
```

### 4) Run
```
# backend
cd backend
python main.py

# frontend
cd frontend
npm run dev
```

## Environment Variables
Create a `.env` for backend (or export in shell):
```
# LLM
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=your_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat

# Optional Ollama fallback
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:8b

# Storage
POSTGRES_DSN=postgresql://graph:graph@localhost:5435/graph
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4jpassword
NEO4J_DATABASE=neo4j

# Chroma (Docker HTTP mode)
CHROMA_HTTP_URL=http://localhost:8001

# Embeddings
# ollama (default) | sentence-transformers | disabled
EMBEDDINGS_PROVIDER=sentence-transformers
ST_EMBEDDINGS_MODEL=all-MiniLM-L6-v2

# OCR / PDF (Windows)
POPPLER_PATH=C:\poppler\Library\bin
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
OCR_AGENT=tesseract

# ASR
WHISPER_MODEL=base
ASR_BACKEND=auto   # auto | openai-whisper | faster-whisper
WHISPER_DEVICE=cpu
WHISPER_COMPUTE_TYPE=int8

# Data dir (local mode only)
DATA_DIR=./app/data
```

## API Cheatsheet

### Ingest (PDF/IFC/Text)
`POST /api/ingest`
- form-data fields:
  - `file` (optional)
  - `text` (optional)
  - `tenant_id` (default: `default`)
  - `llm_provider` (`deepseek` | `ollama`)
  - `llm_model` (optional)
  - `source_type` (optional: `pdf`, `ifc`, `text`)
  - `agent_id` (optional)

Response:
```
{
  "extraction": { ... },
  "markdown": "...",
  "source_type": "pdf",
  "storage": {
    "postgres": true,
    "chroma": true,
    "neo4j": true
  }
}
```

### Agents
- `POST /api/agents` Create Agent
- `GET /api/agents?tenant_id=...` List Agents
- `GET /api/agents/{id}?tenant_id=...` Agent Detail
- `POST /api/agents/{id}/deactivate?tenant_id=...` Deactivate
- `DELETE /api/agents/{id}?tenant_id=...` Delete

### Documents
- `GET /api/documents?tenant_id=...` List Docs
- `GET /api/documents/{id}?tenant_id=...` Doc Detail
- `GET /api/documents/{id}/download?tenant_id=...` Download
- `DELETE /api/documents/{id}?tenant_id=...` Delete

### RAG Chat (streaming)
- `POST /api/chat` JSON body `{ tenant_id, query, language, llm_provider, llm_model }`

### Meeting / ASR
- `POST /api/meeting/ingest` (text)
- `POST /api/meeting/asr` (audio)

### Reports
- `POST /api/report/pdf`
- `POST /api/report/note`

## Multi-Tenancy
- Postgres: `tenant_{tenant_id}` schema per tenant.
- Chroma: `tenant_{tenant_id}` collection per tenant.
- Neo4j: `Tenant_{tenant_id}` label per tenant.

## Notes & Troubleshooting
- Unstructured `hi_res` requires `poppler` + `tesseract` in PATH on Windows.
- Whisper requires `ffmpeg` in PATH.
- Large PDFs can take several minutes on CPU (OCR + layout model).
- If embeddings are slow on CPU, set `EMBEDDINGS_PROVIDER=disabled` to skip Chroma.
