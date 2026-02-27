# MARIS – Multi-Agent Research Intelligence System
## Complete Technical Workflow

---

## 1️⃣ User Interaction Layer (Frontend)

### React (Vite) + Tailwind UI
- User enters research goal
- Calls FastAPI endpoints via Axios:
  - POST /api/research/start
  - POST /api/research/step
  - GET /api/research/state

---

## 2️⃣ API Layer (FastAPI Backend)

### FastAPI Application
- Session-based state management
- CORS enabled
- Stateless REST endpoints
- Routes defined in api/routes.py

Request Flow:
React UI → FastAPI → LangGraph Engine

---

## 3️⃣ Orchestration Layer (LangGraph)

### Shared State Object
All agents operate on:

def run(state: dict) -> dict

Rules:
- Reads global state
- Writes only its own keys
- No direct agent-to-agent communication

LangGraph manages:
- Sequential flow
- Reflection loop
- Conditional branching (gap selection)

---

# 🔬 Core Intelligence Workflow

---

## 🎯 Step 1: Meta Agent (Research Director)

Input:
- research_goal

Processes:
- Query optimization (Gemini)
- Gap scoring framework initialization
- Output validation rules

Output:
- optimized_query
- scoring schema

Services Used:
- gemini_service.py

---

## 📚 Step 2: Literature Agent

Input:
- optimized_query

Processes:
- Fetch 10 papers from arXiv API
- Generate embeddings (sentence-transformers)
- Store vectors (FAISS)
- Run KMeans clustering (scikit-learn)
- Cluster density analysis

Output:
- papers[]
- embeddings
- cluster_analysis
- literature_summary

Services Used:
- arxiv_service.py
- embedding_service.py
- clustering_service.py

---

## 🔗 Step 3: Related Work Agent

Input:
- papers[]
- cluster_analysis

Processes:
- Thematic grouping
- Research landscape mapping
- Structured synthesis

Output:
- related_work_section

Service:
- gemini_service.py

---

## 🎯 Step 4: Gap Detection Agent (Analytical Gap Engine)

Input:
- cluster_analysis
- literature_summary

Processes:
- Detect sparsest cluster
- Identify underexplored research region
- Generate 3–5 gaps
- Assign confidence scores

Output:
- gaps[]
- sparsest_cluster

Service:
- clustering_service.py
- gemini_service.py

---

## 🧪 Step 5: Experiment Design Agent

Input:
- selected_gap
- literature context

Processes:
- Hypothesis generation
- Method design
- Baseline suggestion
- Metric definition
- RIS calculation

### Research Intelligence Score (RIS)

RIS = 0.4 * novelty + 0.3 * feasibility + 0.3 * impact

Novelty:
- Max Euclidean distance from cluster centroid

Feasibility:
- Gemini evaluation

Impact:
- Contribution prediction

Output:
- experiment_plan
- research_scores

Service:
- scoring_service.py
- gemini_service.py

---

## 🔄 Step 6: Reflection Agent (Self-Improvement Loop)

Input:
- experiment_plan
- RIS scores

Processes:
- Weakness detection
- Hypothesis refinement
- RIS recomputation
- Confidence tracking

Output:
- refined_hypothesis
- updated_scores
- improvement_metrics

Service:
- gemini_service.py
- scoring_service.py

---

## 📊 Step 7: Dataset Agent

Input:
- refined_hypothesis

Processes:
- Dataset recommendation
- Availability check
- Alternatives suggestion
- Preprocessing guidance

Output:
- dataset_recommendations

Service:
- gemini_service.py

---

## 📝 Step 8: Paper Drafting Agent

Input:
- refined_hypothesis
- experiment_plan
- dataset_plan

Processes:
- Title generation
- Abstract writing
- Outline creation
- Contribution summary

Output:
- final_draft

Service:
- gemini_service.py

---

# 🗄 Supporting Services

- gemini_service.py → Centralized LLM wrapper (JSON enforced)
- clustering_service.py → KMeans + sparsest cluster detection
- scoring_service.py → RIS formula & scoring logic
- embedding_service.py → Sentence-transformers + FAISS
- arxiv_service.py → arXiv integration

---

# 🔁 Final State Object (Unified Output)

The system produces:

- research_goal
- optimized_query
- cluster_analysis
- selected_gap
- experiment_plan
- RIS scores
- refined_output
- dataset_recommendations
- final_draft
