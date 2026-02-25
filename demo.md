# AI Research Co-Scientist - Demo Script

## Demo Flow (5 minutes)

### 1. Opening (30 seconds)
"Today I'm demoing AI Research Co-Scientist - an AI multi-agent system that helps researchers go from 'I want to publish on X' to a complete paper draft in minutes."

### 2. Start Research (1 minute)
**Action:** Enter research goal in the chat input

**Example Input:**
```
"Few-shot learning for medical image segmentation"
```

**What Happens:**
- Literature Agent queries arXiv API
- Fetches 10 most relevant papers
- LLM analyzes and summarizes key themes

**Expected Output:**
- List of papers with titles, authors, summaries
- Literature summary with key themes and methodologies

### 3. Gap Detection (1 minute)
**Action:** Click "Find Gaps" button

**What Happens:**
- Gap Agent analyzes literature summary
- LLM identifies 3-5 unexplored areas
- Each gap has description, rationale, and impact

**Expected Output:**
```
Gap 0: Limited exploration of cross-modality few-shot learning
Gap 1: Few studies on data efficiency in medical imaging
Gap 2: Underexplored: few-shot with limited annotations
```

### 4. Experiment Design (1 minute)
**Action:** Select Gap 0, click "Design Experiment"

**What Happens:**
- Experiment Agent converts gap to concrete plan
- Generates: hypothesis, dataset, metrics, baselines, proposed method

**Expected Output:**
```json
{
  "hypothesis": "Cross-modality knowledge transfer improves few-shot medical image segmentation",
  "dataset_suggestion": "Combined CT/MRI dataset with 5-class segmentation",
  "metrics": ["Dice Score", "IoU", "Hausdorff Distance"],
  "baseline_methods": ["Prototypical Networks", "MAML", "Standard U-Net"],
  "proposed_method": "Modality-agnostic prototypical network with domain adaptation"
}
```

### 5. Paper Draft (1 minute)
**Action:** Click "Generate Draft"

**What Happens:**
- Drafting Agent synthesizes everything
- Creates: title, abstract, paper outline

**Expected Output:**
```json
{
  "title": "Cross-Modality Prototypical Networks for Few-Shot Medical Image Segmentation",
  "abstract": "Few-shot learning has shown promise in medical imaging...",
  "outline": [
    "Introduction: Challenge of limited labeled data in medical imaging",
    "Related Work: Few-shot learning and medical image segmentation",
    "Method: Cross-modality prototypical networks",
    "Experiments: Evaluation on CT/MRI datasets",
    "Conclusion: Implications for clinical deployment"
  ]
}
```

### 6. Closing (30 seconds)
"In under 5 minutes, we went from a research idea to a complete paper draft with:
- Literature review with 10 papers
- 4 identified research gaps
- Concrete experiment design
- Full paper outline

This is a hackathon MVP - imagine the potential with more agents, real experiments, and full paper generation!"

---

## Architecture Highlights

**Multi-Agent System:**
- 4 specialized agents with strict contracts
- LangGraph orchestration with shared state
- Each agent outputs structured JSON

**Clean Separation:**
- Services layer for external APIs (arXiv, LLM, embeddings)
- Agents don't call APIs directly
- State flows through graph, not agent-to-agent

**Tech Stack:**
- FastAPI + LangGraph backend
- React + Tailwind frontend
- FAISS for vector search

---

## Backup Demo Topics

If the first topic doesn't work well, try these:

1. **"Self-supervised learning for time series forecasting"**
2. **"Reinforcement learning for robotic manipulation"**
3. **"Knowledge distillation for large language models"**
4. **"Graph neural networks for molecular property prediction"**

---

## Troubleshooting

**If arXiv API is slow:**
- Papers may take 10-20 seconds to load
- Have a backup topic ready

**If LLM calls fail:**
- Check API keys in `.env`
- Fallbacks are built into agents

**If frontend won't connect:**
- Ensure backend is running on port 8000
- Check CORS settings in `.env`
