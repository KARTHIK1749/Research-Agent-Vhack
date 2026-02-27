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

## 🔄 Complete MARIS Workflow

### Step-by-Step Research Process

#### 🎯 **Step 1: Meta Agent - Research Director**
**Input:** User's research goal (e.g., "Improving transformer efficiency for long sequences")
- **Query Optimization:** Converts vague goals into arXiv-compatible search queries
- **Gap Quality Scoring:** Evaluates identified gaps on novelty, feasibility, impact, and citation potential
- **Auto-Selection:** Automatically selects best gap if user doesn't specify
- **Output Validation:** Ensures all agent outputs are consistent and feasible

**Output:** Optimized search query + gap scoring framework

---

#### 📚 **Step 2: Literature Agent - Knowledge Discovery**
**Input:** Optimized search query from Meta Agent
- **arXiv Integration:** Fetches 10 relevant papers using optimized query
- **KMeans Clustering:** Groups papers into research landscapes (5 clusters)
- **Embedding Creation:** Generates semantic embeddings for all papers
- **Cluster Analysis:** Identifies density and distribution of research areas
- **Literature Synthesis:** Provides structured analysis with key themes, methodologies, and findings

**Output:** Papers + literature summary + cluster analysis + embeddings

---

#### 🔗 **Step 3: Related Work Agent - Context Analysis**
**Input:** Literature analysis and paper clusters
- **Related Research Synthesis:** Analyzes connections between papers
- **Research Landscape Mapping:** Identifies major research streams and evolution
- **Citation Patterns:** Understands how research builds upon previous work
- **Context Establishment:** Provides foundation for gap identification

**Output:** Comprehensive related work analysis

---

#### 🎯 **Step 4: Gap Detection Agent - Analytical Gap Engine**
**Input:** Literature summary + cluster analysis
- **Sparsest Cluster Detection:** Identifies underexplored research areas using KMeans results
- **Data-Driven Gap Identification:** Uses cluster density instead of manual inspection
- **Gap Prioritization:** Ranks gaps by research potential and feasibility
- **Confidence Scoring:** Provides reliability metrics for each identified gap

**Output:** 3-5 research gaps with confidence scores and sparsest cluster identification

---

#### 🧪 **Step 5: Experiment Design Agent - Hypothesis Generation**
**Input:** Selected research gap + literature context
- **Hypothesis Formulation:** Converts gaps into testable research hypotheses
- **Research Intelligence Score (RIS) Calculation:**
  - **Novelty Score:** Maximum Euclidean distance from cluster centroids
  - **Feasibility Assessment:** Technical complexity evaluation
  - **Impact Prediction:** Potential contribution and applications
  - **Risk Analysis:** Failure probability and challenges
- **Experiment Planning:** Dataset suggestions, metrics, baselines, and proposed methods

**Output:** Research hypothesis + experiment plan + comprehensive RIS scores

---

#### 🔄 **Step 6: Reflection Agent - Self-Refinement Loop**
**Input:** Original hypothesis + RIS scores + experiment plan
- **Weakness Identification:** Detects logical flaws and unrealistic assumptions
- **Hypothesis Refinement:** Proposes improved research hypotheses
- **Iterative Improvement:** Recomputes RIS after reflection
- **Confidence Tracking:** Monitors improvement and reliability metrics
- **Improvement Quantification:** Measures RIS changes and confidence gains

**Output:** Refined hypothesis + improvement metrics + updated RIS scores

---

#### 📊 **Step 7: Dataset Agent - Data Intelligence**
**Input:** Refined hypothesis + experiment requirements
- **Dataset Recommendations:** Suggests appropriate datasets for experiments
- **Data Availability Check:** Verifies accessibility and quality of datasets
- **Alternative Options:** Provides backup dataset choices
- **Data Preparation Guidance:** Offers preprocessing and formatting advice

**Output:** Dataset recommendations + data preparation guidelines

---

#### 📝 **Step 8: Paper Drafting Agent - Research Synthesis**
**Input:** Refined hypothesis + dataset plan + complete research context
- **Title Generation:** Creates compelling and accurate paper titles
- **Abstract Writing:** Summarizes research contribution and methodology
- **Outline Creation:** Provides structured paper outline with sections
- **Key Contributions:** Highlights novel aspects and practical implications

**Output:** Complete paper draft (title, abstract, outline)

---

### 🎯 **Workflow Visualization**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Query    │───▶│   Meta Agent     │───▶│ Literature Agent│
│                 │    │ (Query Optimize) │    │ (arXiv + Cluster)│
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                        │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Paper Draft     │◀───│  Dataset Agent   │◀───│Reflection Agent │
│ (Title+Abstract)│    │ (Data Recs)      │    │ (Self-Refine)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         ▲                                              │
         │                    ┌──────────────────┐      │
         └────────────────────│ Experiment Agent │◀─────┘
                              │ (RIS Scoring)   │
                              └──────────────────┘
                                       ▲
┌─────────────────┐    ┌──────────────────┐      │
│ Related Work    │◀───│  Gap Detection   │◀─────┘
│ Agent           │    │ (Analytical Gap) │
└─────────────────┘    └──────────────────┘
```

### 🔄 **Key Workflow Features**

#### **Intelligence Loop Integration**
- **Meta Agent** orchestrates entire workflow with quality control
- **Reflection Loop** provides iterative improvement capability
- **RIS Scoring** quantifies research quality at multiple stages
- **Cluster Analysis** drives data-driven gap identification

#### **Quality Assurance**
- **Output Validation** ensures consistency between agents
- **Gap Scoring** provides quantitative gap evaluation
- **Confidence Metrics** track reliability throughout process
- **Improvement Tracking** measures refinement benefits

#### **User Interaction Points**
- **Gap Selection:** User can choose specific research gap
- **Hypothesis Review:** User can review and refine hypotheses
- **Dataset Approval:** User can approve or modify dataset choices
- **Draft Customization:** User can modify paper drafts

### 📊 **Workflow Output Summary**

Each step produces specific outputs that feed into the next stage:

1. **Meta:** Optimized query + scoring framework
2. **Literature:** Papers + clusters + embeddings + analysis
3. **Related Work:** Contextual research landscape
4. **Gap Detection:** Data-driven gaps with confidence scores
5. **Experiment:** Hypothesis + RIS scores + experiment plan
6. **Reflection:** Refined hypothesis + improvement metrics
7. **Dataset:** Data recommendations + preparation guidance
8. **Drafting:** Complete paper draft ready for submission

This workflow ensures comprehensive research coverage from initial idea to final paper, with intelligence and quality control at every step.

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
