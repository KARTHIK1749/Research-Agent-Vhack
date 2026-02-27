# MARIS (Multi-Agent Research Intelligence System)

A hackathon-ready, production-style MVP for MARIS with advanced AI research capabilities including analytical gap detection, research intelligence scoring, and self-reflection loops.

## 🚀 MARIS Features

### Core Agents
- **Meta Agent / Research Director**: Optimizes queries, scores gaps, validates outputs, auto-selects best gap
- **Literature Agent**: Fetches relevant papers from arXiv with clustering analysis
- **Gap Detection Agent**: Identifies unexplored research areas using analytical gap engine
- **Experiment Design Agent**: Converts gaps into concrete, testable hypotheses with RIS scoring
- **Reflection Agent**: Self-reflection loop for hypothesis refinement and improvement
- **Paper Drafting Agent**: Generates title, abstract, and outline
- **Dataset Agent**: Recommends and manages datasets for experiments
- **Related Work Agent**: Analyzes and synthesizes related research papers

### 🧠 MARIS Intelligence Features

#### Analytical Gap Engine
- **KMeans Clustering**: Automatically clusters research papers to identify research landscapes
- **Sparsest Cluster Detection**: Finds underexplored research areas with low paper density
- **Data-Driven Gap Identification**: Uses cluster analysis instead of manual inspection

#### Research Intelligence Score (RIS)
- **Novelty Score**: Computed as maximum Euclidean distance from cluster centroids
- **Feasibility Assessment**: Gemini-powered evaluation of technical complexity
- **Impact Prediction**: Assessment of potential contribution and practical applications
- **Risk Analysis**: Probability of failure and technical challenges
- **Weighted Formula**: `RIS = 0.4 * novelty + 0.3 * feasibility + 0.3 * impact`

#### Self-Reflection Loop
- **Weakness Identification**: Detects logical flaws and unrealistic assumptions
- **Hypothesis Refinement**: Proposes improved research hypotheses
- **Iterative Improvement**: Recomputes RIS after reflection
- **Confidence Scoring**: Tracks improvement and reliability metrics

### 🎯 Enhanced Workflow
```
User Query
    ↓
Meta Agent (Query Optimization)
    ↓
Literature Agent (arXiv + Clustering Analysis)
    ↓
Gap Detection Agent (Analytical Gap Engine)
    ↓
Experiment Design Agent (RIS Scoring)
    ↓
Reflection Agent (Self-Refinement Loop)
    ↓
Dataset Agent (Data Recommendations)
    ↓
Paper Drafting Agent (Final Output)
```

## Tech Stack

**Backend:**
- Python + FastAPI
- LangGraph for multi-agent orchestration
- **Gemini API** (Gemini-only, OpenAI removed)
- arXiv API for literature retrieval
- FAISS for vector similarity search
- **scikit-learn** for KMeans clustering
- **sentence-transformers** for embeddings

**MARIS Intelligence Services:**
- **clustering_service.py** - Analytical Gap Engine
- **scoring_service.py** - Research Intelligence Score calculation
- **gemini_service.py** - Centralized LLM wrapper with JSON enforcement
- **embedding_service.py** - Paper embeddings and similarity search

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
maris/
├── backend/
│   ├── app/
│   │   ├── agents/           # 8 specialized agents
│   │   │   ├── literature_agent.py      # + clustering analysis
│   │   │   ├── gap_agent.py             # + analytical gap engine
│   │   │   ├── experiment_agent.py      # + RIS scoring
│   │   │   ├── reviewer_agent.py        # → reflection_agent.py
│   │   │   └── ...
│   │   ├── api/              # FastAPI routes
│   │   ├── graph/            # LangGraph orchestration (+ reflection loop)
│   │   ├── models/           # Pydantic schemas
│   │   ├── services/         # Enhanced external services
│   │   │   ├── clustering_service.py     # 🆕 Analytical Gap Engine
│   │   │   ├── scoring_service.py        # 🆕 RIS calculation
│   │   │   ├── gemini_service.py         # 🆕 Centralized Gemini wrapper
│   │   │   ├── embedding_service.py      # Enhanced embeddings
│   │   │   ├── arxiv_service.py          # arXiv integration
│   │   │   └── llm_service.py            # Legacy → Gemini forwarder
│   │   ├── utils/            # Prompts
│   │   └── main.py           # Entry point
│   ├── requirements.txt     # + scikit-learn, google-generativeai
│   └── .env                 # Gemini API key only
│
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/            # Page components
│   │   └── services/         # API service layer
│   ├── package.json
│   └── index.html
│
├── README.md                 # 🆕 Updated with new features
└── demo.md                   # Demo script
```

## MARIS Agent Workflow

```
User Query
    ↓
Meta Agent (Query Optimization + Gap Scoring + Validation)
    ↓
Literature Agent (arXiv fetch + Clustering Analysis)
    ↓
Related Work Agent (analyze related research)
    ↓
Gap Detection Agent (Analytical Gap Engine + Sparsest Cluster)
    ↓
Experiment Design Agent (Hypothesis + RIS Scoring)
    ↓
Reflection Agent (Self-Refinement Loop + RIS Recalculation)
    ↓
Dataset Agent (Data Recommendations)
    ↓
Paper Drafting Agent (Title + Abstract + Outline)
```

## 🆕 MARIS Output Format

The final state now includes comprehensive research intelligence:

```json
{
  "research_goal": "Improving transformer efficiency for long sequences",
  "selected_gap": {
    "title": "Sparsest Research Area",
    "description": "Underexplored approach identified by clustering",
    "confidence": 0.85
  },
  "hypothesis": "Original research hypothesis",
  "experiment_plan": {
    "hypothesis": "...",
    "dataset_suggestion": "...",
    "metrics": ["...", "..."],
    "baseline_methods": ["...", "..."],
    "proposed_method": "..."
  },
  "research_scores": {
    "novelty": 8.2,
    "feasibility": 7.5,
    "impact": 8.8,
    "risk": 4.2,
    "ris": 8.1
  },
  "refined_output": {
    "criticisms": ["Weakness 1", "Weakness 2"],
    "refined_hypothesis": "Improved research hypothesis",
    "confidence": 0.92,
    "improvement": {
      "ris_change": +0.8,
      "novelty_change": +0.5,
      "feasibility_change": +0.3
    }
  },
  "final_ris": 8.9,
  "cluster_analysis": {
    "density": {0: 3, 1: 2, 2: 1, 3: 4},
    "sparsest_cluster": 2,
    "n_clusters": 5
  }
}
```

## Agent Contract

Every agent follows this structure:
```python
def run(state: dict) -> dict:
    """Takes graph state, updates ONLY its own keys, returns updated state."""
    # Agent logic here
    state["agent_output"] = result
    return {"status": "healthy", "service": "maris"}
```

## 🆕 MARIS Demo Flow

1. Enter research goal: *"Improving transformer efficiency for long sequences"*
2. Literature Agent fetches 10 relevant papers and performs **KMeans clustering**
3. **Analytical Gap Engine** identifies sparsest research cluster
4. Gap Detection generates **cluster-based gaps** with confidence scores
5. User selects a gap (or defaults to sparsest cluster)
6. Experiment Design creates hypothesis and computes **RIS scores**
7. **Reflection Agent** analyzes weaknesses and **refines hypothesis**
8. RIS is **recomputed** for refined hypothesis
9. Paper Drafting generates title, abstract, and outline

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` | Yes | Gemini API key (OpenAI removed) |
| `BACKEND_PORT` | No | Backend port (default: 8000) |
| `CORS_ORIGINS` | No | Allowed origins |

### 🆕 MARIS Dependencies

Updated `requirements.txt` includes:
- `scikit-learn` - For KMeans clustering
- `google-generativeai` - Direct Gemini API integration
- `sentence-transformers` - Enhanced embeddings
- All original dependencies maintained

## License

MIT License - Built for hackathons.
