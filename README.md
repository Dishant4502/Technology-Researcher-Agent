# Technology Autonomous Researcher

An LLM-powered autonomous researcher for the technology industry. The stack combines a Python API, LangChain-powered web search, CrewAI multi-agent synthesis, and a React dashboard for launching research runs and browsing archived knowledge entries.

## Architecture

- `backend/`: FastAPI service that orchestrates search, CrewAI analysis, and knowledge persistence.
- `backend/knowledge_repo/`: Text-based repository that stores generated markdown research briefs plus an index.
- `frontend/`: React + Vite interface for submitting queries and viewing outputs.

## Backend workflow

1. Accept a research query and desired analysis depth.
2. Search the web with Tavily when configured, otherwise fall back to DuckDuckGo via LangChain community tools.
3. Build a CrewAI pipeline with three agents:
   - Research Scout
   - Industry Analyst
   - Knowledge Curator
4. Generate a markdown report with citations and strategic takeaways.
5. Persist the report to `backend/knowledge_repo/` and register metadata in `index.json`.

## Setup

### 1. Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Set the required environment variables in `backend/.env`:

- `GROQ_API_KEY`: API key for Groq (preferred).
- `GROQ_MODEL`: Groq model name for CrewAI synthesis.
- `GROQ_BASE_URL`: Groq OpenAI-compatible base URL (default: `https://api.groq.com/openai/v1`).
- `OPENAI_API_KEY`: Optional fallback if Groq key is not set.
- `OPENAI_MODEL`: Optional fallback model.
- `OPENAI_BASE_URL`: Optional fallback base URL.
- `TAVILY_API_KEY`: Optional, enables stronger web search than the DuckDuckGo fallback.
- `ALLOWED_ORIGINS`: Comma-separated frontend origins if you deploy elsewhere.

Start the API:

```powershell
uvicorn app.main:app --reload --port 8000
```

Open `http://localhost:8000/docs` to verify the backend is running. The backend does not render the React UI.

### 2. Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open the UI at `http://localhost:5173`.

If your API is not at `http://localhost:8000`, create `frontend/.env` with:

```bash
VITE_API_BASE=http://localhost:8000/api
```

## API

- `GET /health`
- `POST /api/research`
- `GET /api/research/entries`

Example request:

```json
{
  "query": "What are the most important shifts in enterprise AI platforms this quarter?",
  "depth": "advanced",
  "source_limit": 6
}
```

## Notes

- The backend is written to support current web search through LangChain tools and report synthesis through CrewAI.
- The repository intentionally stores plain markdown files so results stay auditable and easy to reuse.
- For production, add authentication, rate limiting, richer markdown rendering, and source deduplication.
