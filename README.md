# AI Research Co-Scientist

A hackathon-ready, production-style MVP for an AI multi-agent system that helps researchers go from idea to paper draft.

## Features

- **Meta Agent / Research Director**: Optimizes queries, scores gaps, validates outputs, auto-selects best gap
- **Literature Agent**: Fetches relevant papers from arXiv and analyzes them
- **Gap Detection Agent**: Identifies unexplored research areas
- **Experiment Design Agent**: Converts gaps into concrete, testable hypotheses
- **Paper Drafting Agent**: Generates title, abstract, and outline

## Tech Stack

**Backend:**
- Python + FastAPI
- LangGraph for multi-agent orchestration
- Gemini/OpenAI for LLM calls
- arXiv API for literature retrieval
- FAISS for vector similarity search

**Frontend:**
- React (Vite)
- Tailwind CSS
- Axios for API calls

## Quick Start

### 1. Setup Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` file:
```
GOOGLE_API_KEY=your_gemini_api_key_here
# OR
OPENAI_API_KEY=your_openai_api_key_here
BACKEND_PORT=8000
CORS_ORIGINS=http://localhost:5173
```

Start the server:
```bash
python -m app.main
# OR
uvicorn app.main:app --reload
```

### 2. Setup Frontend

```bash
cd frontend
npm install
npm run dev
```

### 3. Access the App

Open http://localhost:5173 in your browser.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/research/start` | POST | Start new research session |
| `/api/research/step` | POST | Execute next workflow step |
| `/api/research/state` | GET | Get current session state |
| `/health` | GET | Health check |

## Project Structure

```
ai-research-co-scientist/
├── backend/
│   ├── app/
│   │   ├── agents/           # 4 modular agents
│   │   ├── api/              # FastAPI routes
│   │   ├── graph/            # LangGraph orchestration
│   │   ├── models/           # Pydantic schemas
│   │   ├── services/         # External services (arXiv, LLM, embeddings)
│   │   ├── utils/            # Prompts
│   │   └── main.py           # Entry point
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/            # Page components
│   │   └── services/         # API service layer
│   ├── package.json
│   └── index.html
│
├── README.md
└── demo.md
```

## Agent Workflow

```
User Query
    ↓
Meta Agent (Query Optimization + Gap Scoring + Validation)
    ↓
Literature Agent (arXiv fetch + analysis)
    ↓
Gap Detection Agent (identify research gaps)
    ↓
Experiment Design Agent (hypothesis + methodology)
    ↓
Paper Drafting Agent (title + abstract + outline)
```

## Agent Contract

Every agent follows this structure:
```python
def run(state: dict) -> dict:
    """Takes graph state, updates ONLY its own keys, returns updated state."""
    # Agent logic here
    state["agent_output"] = result
    return state
```

## Demo Flow

1. Enter research goal: *"Improving transformer efficiency for long sequences"*
2. Literature Agent fetches 10 relevant papers from arXiv
3. Gap Detection identifies 3-5 unexplored areas
4. User selects a gap (or defaults to first)
5. Experiment Design creates concrete hypothesis and methodology
6. Paper Drafting generates title, abstract, and outline

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` | Yes* | Gemini API key |
| `OPENAI_API_KEY` | Yes* | OpenAI API key |
| `BACKEND_PORT` | No | Backend port (default: 8000) |
| `CORS_ORIGINS` | No | Allowed origins |

*Only one LLM provider key is required.

## License

MIT License - Built for hackathons.
