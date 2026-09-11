# Veritas: Multi-Agent Research and Fact Verification System

An AI-powered, decoupled Multi-Agent research and fact-verification platform built for students, researchers, and journalists. Operating on the core principle: **"VERIFY FIRST, ANSWER SECOND."**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Deployed on Render](https://img.shields.io/badge/Deploy-Render-46E3B7.svg)](https://render.com)
[![Deployed on Vercel](https://img.shields.io/badge/Deploy-Vercel-black.svg)](https://vercel.com)

> 📖 **Full Academic Project Report & Viva Voce Guide**:  
> For in-depth architecture diagrams, mathematical equations, truth tables, and examiner Q&A, see [`PROJECT_DOCUMENTATION.md`](./PROJECT_DOCUMENTATION.md).

---

## 🌟 Key Highlights

- **Decoupled Multi-Agent Architecture**: 10 specialized agent modules operating synchronously without circular dependencies or hallucinated sources.
- **Natural Language Inference (NLI)**: Integrated `cross-encoder/nli-deberta-v3-xsmall` evaluating premise-hypothesis entailment and contradiction directly on CPU (~50ms latency).
- **Symbolic Mathematical Engine**: Evaluates arithmetic expressions and equation claims via SymPy and Python AST parser without guessing. Automatically disproves false equations (e.g., `2 + 2 = 5` $\rightarrow$ **FALSE**, Correct: `2 + 2 = 4`).
- **Negation & Proposition Inversion**: Algebraic truth-table reasoning for negative claims ($S = \neg P$ is TRUE iff proposition $P$ is false, e.g., *"The Sun does not rise in the west"* $\rightarrow$ **TRUE**, *"Water does not contain oxygen"* $\rightarrow$ **FALSE**).
- **Universal Quantifier Counterexamples**: Identifies counterexamples for strict claims (*all*, *every*, *always*, e.g., *"All birds can fly"* $\rightarrow$ **FALSE** due to penguins/ostriches).
- **Institutional Source Hierarchy**: Audits and scores evidence across 6 credibility tiers (Government, Academic, Scientific Institutions, Encyclopedias, Reputable News, General Web).
- **Editorial Research Workbench UI**: Two-column layout in warm parchment tones featuring a 12-point quality checklist, interactive source inspector, and persistent `localStorage` verification history.
- **18 Automated Benchmark Tests**: 100% test coverage across 8 domains via `pytest`.

---

## 📐 System Architecture

```
                                [ User Statement / Query ]
                                            │
                                            ▼
                           ┌──────────────────────────────────┐
                           │   Step 1: Input Classifier &     │
                           │   Adversarial Suffix Stripper    │
                           └────────────────┬─────────────────┘
                                            │
               ┌────────────────────────────┼────────────────────────────┐
               ▼                            ▼                            ▼
      [ Mathematical Claim ]       [ Compound Statement ]       [ Factual Claim ]
               │                            │                            │
               ▼                            ▼                            │
      ┌─────────────────┐          ┌─────────────────┐                   │
      │ Step 4: SymPy & │          │ Step 12: Claim  │                   │
      │  AST Calculator │          │ Separator Agent │                   │
      └────────┬────────┘          └────────┬────────┘                   │
               │                            │ (Decomposes into Subclaims)│
               │                            ▼                            │
               │                   ┌─────────────────┐                   │
               │                   │ Recursive Eval  │                   │
               │                   └────────┬────────┘                   │
               │                            │                            │
               │                            ▼                            ▼
               │                   ┌───────────────────────────────────────────┐
               │                   │ Step 13: Universal Research Agent         │
               │                   │ (Wikipedia API, DuckDuckGo, Benchmarks)   │
               │                   └─────────────────────┬─────────────────────┘
               │                                         │
               │                                         ▼
               │                   ┌───────────────────────────────────────────┐
               │                   │ Step 2 & 9: Negation Analyzer & Normalizer│
               │                   │ (Polarity detection, Proposition extraction)│
               │                   └─────────────────────┬─────────────────────┘
               │                                         │
               │                                         ▼
               │                   ┌───────────────────────────────────────────┐
               │                   │ Steps 5-8, 10, 11: DeBERTa-v3 NLI Engine  │
               │                   │ (Entailment, Contradiction, Neutral)      │
               │                   └─────────────────────┬─────────────────────┘
               │                                         │
               │                                         ▼
               │                   ┌───────────────────────────────────────────┐
               │                   │ Step 16: Fact Verifier Agent              │
               │                   │ (Initial Verdict & Narrative Synthesis)   │
               │                   └─────────────────────┬─────────────────────┘
               │                                         │
               │                                         ▼
               │                   ┌───────────────────────────────────────────┐
               │                   │ Step 17: Evidence Validator Agent         │
               │                   │ (Source Thresholds & Calibrated Confidence)│
               │                   └─────────────────────┬─────────────────────┘
               │                                         │
               │                                         ▼
               │                   ┌───────────────────────────────────────────┐
               │                   │ Step 18: Quality Guard Agent              │
               │                   │ (Anti-Hallucination & Proposition Inversion)│
               │                   └─────────────────────┬─────────────────────┘
               ▼                                         ▼
    ┌───────────────────────────────────────────────────────────────────────────┐
    │                      Orchestration Response Builder                       │
    └─────────────────────────────────────┬─────────────────────────────────────┘
                                          │
                                          ▼
                       [ Natural Research Workbench UI ]
           - Verdict Badge (TRUE / FALSE / PARTIALLY TRUE / UNVERIFIED)
           - Calibrated Confidence (%) & Clear Narrative Explanation
           - Correct Ground-Truth Statement (for FALSE claims)
           - 12-Point Multi-Agent Quality Audit Checklist
           - Interactive Source Inspector & Persistent LocalStorage History
```

---

## 🤖 Specialized Multi-Agent Breakdown

| Agent Module | Responsibility | Methodology / Technology |
|---|---|---|
| **Input Classifier Agent** (`classifier_agent.py`) | Strips adversarial bias tokens (`"true"`, `"false"`) and categorizes claims into 15 semantic domains. | Regex token extraction & syntax analysis |
| **Calculation Agent** (`calculator_agent.py`) | Deterministic arithmetic equality, inequalities, and percentage checks without LLM guessing. | SymPy & Python AST parser |
| **Research Agent** (`research_agent.py`) | Gathers corroborating/contradicting evidence across Wikipedia, live web, and curated datasets. | Wikipedia API, DuckDuckGo (`ddgs`), Benchmark JSON |
| **Claim Normalizer Agent** (`normalizer_agent.py`) | Cleans and standardizes raw user text by stripping redundant punctuation and whitespace. | String normalization pipeline |
| **Negation Detector Agent** (`negation_agent.py`) | Detects negative polarity (`not`, `never`, `cannot`) and extracts the underlying affirmative proposition. | Linguistic polarity analyzer |
| **Semantic NLI Agent** (`semantic_nli_agent.py`) | Neural premise-hypothesis evaluation ($P(\text{Contra}), P(\text{Entail}), P(\text{Neut})$). | `cross-encoder/nli-deberta-v3-xsmall` |
| **Fact Verifier Agent** (`verifier_agent.py`) | Maps NLI relations to verdicts and formulates evidence-backed factual explanations. | Evidence cross-referencing & synthesis |
| **Evidence Validator Agent** (`validator_agent.py`) | Audits evidence thresholds and calibrates confidence scores against institutional tiers. | Citation threshold auditor |
| **Verification Guard Agent** (`guard_agent.py`) | Enforces proposition inversion consistency and mandates correct counter-statements for FALSE claims. | Logical consistency guard (Step 18) |
| **Answer Agent** (`answer_agent.py`) | Formats clean user-facing summaries and decomposes multi-claim responses. | Response formatter |

---

## 🏆 18-Test Benchmark Suite

The project includes an automated test suite verifying all 18 core evaluation benchmarks:

| # | Test Statement | Category | Expected Verdict | Verified Result |
|---|---|---|---|---|
| 1 | `India became independent in 1947 true` | Adversarial Suffix | **TRUE** | Strips suggested `"true"`, validates 1947 independence |
| 2 | `2 + 2 = 5 false` | Math + Adversarial | **FALSE** | Strips `"false"`, calculates $4 \ne 5$, corrects to `2 + 2 = 4` |
| 3 | `Water does not contain oxygen.` | Scientific Negation | **FALSE** | Proposition ($H_2O$ contains O) is true $\rightarrow$ claim is FALSE |
| 4 | `The Sun does not rise in the west.` | Planetary Negation | **TRUE** | Proposition (rises in west) is false $\rightarrow$ claim is TRUE |
| 5 | `India is not in Europe.` | Geographic Negation | **TRUE** | Proposition (in Europe) is false $\rightarrow$ claim is TRUE |
| 6 | `India is not in Asia.` | Geographic Negation | **FALSE** | Proposition (in Asia) is true $\rightarrow$ claim is FALSE |
| 7 | `Humans cannot breathe underwater without equipment.` | Biological Law | **TRUE** | Validates pulmonary respiration requirement |
| 8 | `2 + 2 = 4` | Arithmetic Equality | **TRUE** | SymPy evaluates $2 + 2 == 4 \rightarrow \text{True}$ |
| 9 | `10 × 5 = 50` | Arithmetic Multiply | **TRUE** | SymPy evaluates $10 \times 5 == 50 \rightarrow \text{True}$ |
| 10 | `100 is less than 20` | Inequality Comparison | **FALSE** | Computes $100 < 20 \rightarrow \text{False}$. Corrects to $100 > 20$ |
| 11 | `25% of 200 is 50` | Percentage Arithmetic | **TRUE** | Computes $0.25 \times 200 == 50 \rightarrow \text{True}$ |
| 12 | `All birds can fly.` | Universal Quantifier | **FALSE** | Flightless counterexamples identified (penguins, ostriches) |
| 13 | `The Pacific Ocean is larger than the Atlantic Ocean.` | Comparison | **TRUE** | Area comparison ($165\text{M km}^2 > 106\text{M km}^2$) confirmed |
| 14 | `The Atlantic Ocean is larger than the Pacific Ocean.` | Comparison | **FALSE** | Area comparison contradiction detected |
| 15 | `India became independent in 1947 and Mumbai is the capital of India.` | Multiple Claims | **FALSE** | Claim 1 is TRUE, Claim 2 is FALSE $\rightarrow$ Overall FALSE |
| 16 | `Fish do not live in water.` | Biological Negation | **FALSE** | Aquatic habitat proposition is true $\rightarrow$ claim is FALSE |
| 17 | `Fish do not live on land.` | Biological Negation | **TRUE** | Terrestrial habitat proposition is false $\rightarrow$ claim is TRUE |
| 18 | `freezing of water will not turns into ice` | Physical Law | **FALSE** | Thermodynamic phase transition contradiction |

---

## 📁 Project Structure

```
Minor Project new/
├── backend/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── classifier_agent.py      # Agent 1: Input Classifier & Suffix Stripper
│   │   ├── calculator_agent.py      # Agent 2: Symbolic Math & AST Calculator
│   │   ├── research_agent.py        # Agent 3: Multi-Source Web & Benchmark Researcher
│   │   ├── normalizer_agent.py      # Agent 4: Text Normalization
│   │   ├── negation_agent.py        # Agent 5: Polarity & Proposition Inversion
│   │   ├── semantic_nli_agent.py    # Agent 6: DeBERTa-v3 Neural NLI Reasoner
│   │   ├── verifier_agent.py        # Agent 7: Fact Verifier & Evidence Cross-Referencer
│   │   ├── validator_agent.py       # Agent 8: Evidence Validator & Calibrator
│   │   ├── guard_agent.py           # Agent 9: Step 18 Quality Guard
│   │   └── answer_agent.py          # Agent 10: Response Formatter
│   ├── core/
│   │   ├── __init__.py
│   │   ├── models.py                # Pydantic schemas & response models
│   │   ├── orchestrator.py          # Multi-Agent 18-step pipeline orchestrator
│   │   └── source_ranker.py         # Institutional credibility tiering & scoring
│   ├── data/
│   │   └── benchmark_facts.json     # Ground truth benchmark database
│   ├── api.py                       # FastAPI application & REST endpoints
│   └── config.py                    # Environment & configuration settings
├── frontend/
│   ├── index.html                   # Two-Column Editorial Research Workbench UI
│   ├── style.css                    # Warm parchment & editorial styling
│   └── app.js                       # Two-column UI state, API bridge, localStorage history
├── tests/
│   ├── __init__.py
│   └── test_agents.py               # 18 automated test cases (pytest)
├── api/
│   └── index.py                     # Vercel Serverless Function entry point
├── Procfile                         # Cloud container start command (Render/Railway)
├── render.yaml                      # Render Blueprint infrastructure-as-code
├── vercel.json                      # Vercel deployment & route rewriting configuration
├── requirements.txt                 # Project dependencies
├── run.py                           # Single-command application launcher
├── PROJECT_DOCUMENTATION.md         # Comprehensive viva report & technical manual
└── README.md
```

---

## 🚀 Quickstart & Local Setup

### 1. Prerequisites
- Python 3.9+ installed on your system.
- Git.

### 2. Clone & Install Dependencies
```bash
git clone https://github.com/Keerthana-06-wq/Multi-agent-research-and-fact-verification-system.git
cd "Minor Project new"
pip install -r requirements.txt
```

### 3. Run Automated Tests
```bash
python -m pytest tests/test_agents.py -v
```
*(All 18 tests will execute and pass cleanly).*

### 4. Launch the Web Application
```bash
python run.py
```

### 5. Open in Browser
- **Web Interface**: 👉 [http://localhost:8000/](http://localhost:8000/)
- **Interactive OpenAPI Documentation**: 👉 [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check**: 👉 [http://localhost:8000/health](http://localhost:8000/health)

---

## ☁️ Cloud Deployment

### Deploy to Render
The repository includes `render.yaml` and `Procfile`.
1. Go to [dashboard.render.com](https://dashboard.render.com/) and click **"New +"** $\rightarrow$ **"Web Service"**.
2. Connect this GitHub repository.
3. Render auto-detects `render.yaml` and starts:
   `uvicorn backend.api:app --host 0.0.0.0 --port $PORT`
4. Both the frontend and backend will be live at `https://your-service.onrender.com`.

### Deploy to Vercel
The repository includes `api/index.py` and `vercel.json`.
1. Import this repository into [vercel.com](https://vercel.com).
2. Vercel automatically deploys the static frontend from `/frontend` and routes API requests to the Python serverless function.

---

## 📄 License
This project is licensed under the MIT License — free for academic, research, and educational use.
