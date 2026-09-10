# Multi-Agent Research and Facts Verification System (VERITAS)

An AI-powered, decoupled Multi-Agent research and fact-verification platform built for students, researchers, and journalists. Built for college minor project demonstrations with rigorous evidence cross-referencing and mathematical calculation.

Operating on the core principle: **"VERIFY FIRST, ANSWER SECOND."**

---

## Key Highlights

- **Decoupled Multi-Agent Architecture**: 6 specialized agents working synchronously without circular dependencies or hallucinated sources.
- **Natural, Professional Research UI**: Publication-grade research portal aesthetic designed for academic and journalistic use (NO chatbot toys, NO neon futuristic glow, NO fake AI-thinking animations).
- **Independent Mathematical Engine**: Evaluates arithmetic expressions and equation claims via SymPy and AST analysis without guessing. Automatically disproves false equations (e.g., `2 + 2 = 5` $\rightarrow$ **FALSE**, Correct: `2 + 2 = 4`).
- **Citation-Backed Verification**: Ranks evidence across 6 institutional tiers (Government, Academic, Scientific Institutions, Encyclopedic Reference, Reputable News, General Web).
- **Preset Evaluation Suite**: 10 one-click evaluation benchmarks built directly into the UI.

---

## System Architecture

```
                                [ User Input ]
                                      │
                                      ▼
                     ┌──────────────────────────────────┐
                     │  Agent 1: Input Classifier Agent │
                     └────────────────┬─────────────────┘
                                      │
         ┌────────────────────────────┼────────────────────────────┐
         ▼                            ▼                            ▼
  ┌──────────────┐             ┌────────────────┐          ┌─────────────────┐
  │   Agent 2:   │             │    Agent 3:    │          │    Agent 6:     │
  │  Calculation │             │ Research Agent │          │ Informational / │
  │    Agent     │             │ (Web + Wiki +  │          │   Answer Agent  │
  │ (SymPy / AST)│             │  Gov/Academic) │          └────────┬────────┘
  └──────┬───────┘             └───────┬────────┘                   │
         │                             ▼                            │
         │                     ┌────────────────┐                   │
         │                     │    Agent 4:    │                   │
         │                     │ Fact Verifier  │                   │
         │                     └───────┬────────┘                   │
         │                             ▼                            │
         │                     ┌────────────────┐                   │
         │                     │    Agent 5:    │                   │
         │                     │Evidence Valid- │                   │
         │                     │  ator Agent    │                   │
         │                     └───────┬────────┘                   │
         ▼                             ▼                            ▼
   ┌───────────────────────────────────────────────────────────────────┐
   │             Agent Pipeline Orchestrator & Formatter               │
   └───────────────────────────────────┬───────────────────────────────┘
                                       ▼
                       [ Natural Research Portal UI ]
            - Status Badges: TRUE, FALSE, PARTIALLY TRUE, UNVERIFIED
            - Highlighted Correct Statement (for FALSE / PARTIAL claims)
            - Evidence Snippets & Ranked Source Citations
            - Transparent Agent Execution Trace
```

---

## Specialized Agent Breakdown

| Agent | Responsibility | Core Tech / Methodology |
|---|---|---|
| **Agent 1: Input Classification Agent** | Analyzes syntax and intent to categorize input into Pure Calculation, Math Claim, Factual Claim, Factual Query, General Question, or Opinion. Strips user confirmation biases. | Regex & NLP Pattern Parser |
| **Agent 2: Calculation Agent** | Evaluates mathematical equations and expressions without guessing. Compares LHS and RHS independently for math claims. | SymPy & Python AST parser |
| **Agent 3: Research Agent** | Gathers corroborating and contradicting evidence from authoritative channels, ranking source institutional authority. | Wikipedia API, DuckDuckGo (`ddgs`), Benchmark Ground-Truth |
| **Agent 4: Fact Verification Agent** | Evaluates claims against gathered evidence, establishing verdicts (`TRUE`, `FALSE`, `PARTIALLY TRUE`, `UNVERIFIED`) and extracting accurate corrections. | Semantic Evidence Cross-Referencing |
| **Agent 5: Evidence Validator Agent** | Audits verifier output against raw source citations to enforce anti-hallucination and prevent unwarranted confidence. | Citation & Threshold Auditor |
| **Agent 6: Informational Answer Agent** | Provides structured, educational answers to conceptual inquiries (e.g., *"What is artificial intelligence?"*). | Curated Knowledge Base & Encyclopedias |

---

## Source Credibility Hierarchy

Sources are categorized and weighted based on institutional authority:

1. **Government (`Tier 1`)**: `.gov`, `.gov.in`, `.nic.in`, `.gov.uk` (Score: 95–100%)
2. **Academic & Universities (`Tier 2`)**: `.edu`, `.ac.in`, `arxiv.org`, `jstor.org` (Score: 90–95%)
3. **Scientific Institutions (`Tier 3`)**: NASA, WHO, CERN, ISRO, NOAA, NIH (Score: 95–98%)
4. **Reference & Encyclopedias (`Tier 4`)**: Wikipedia, Britannica, Oxford Reference (Score: 85–90%)
5. **Reputable News Agencies (`Tier 5`)**: Reuters, AP News, BBC, The Hindu, NYT (Score: 80–85%)
6. **General Web (`Tier 6`)**: General indexed websites (Score: 50–65%)

---

## Evaluation Benchmark Suite

The project includes an automated test suite verifying all 10 core requirements:

| # | Test Query | Category | Expected Verdict | Verified Result |
|---|---|---|---|---|
| 1 | `2 + 2 = 5` | Math Claim | `FALSE` | Correct statement: `2 + 2 = 4` |
| 2 | `2 + 2 = 4` | Math Claim | `TRUE` | Evaluated equality |
| 3 | `The Earth revolves around the Sun.` | Factual Claim | `TRUE` | Heliocentric orbital model confirmed |
| 4 | `The Sun revolves around the Earth.` | Factual Claim | `FALSE` | Correct: `The Earth revolves around the Sun.` |
| 5 | `New Delhi is the capital of India.` | Factual Claim | `TRUE` | Validated national capital |
| 6 | `Mumbai is the capital of India.` | Factual Claim | `FALSE` | Correct: `New Delhi is the capital of India.` |
| 7 | `Aliens built the pyramids in 10,000 BC.` | Unsubstantiated Claim | `UNVERIFIED` | Insufficient scientific evidence |
| 8 | `Thomas Edison invented the light bulb and the internet.` | Partially True Claim | `PARTIALLY TRUE` | Identifies light bulb as valid, internet as false |
| 9 | `What is artificial intelligence?` | Informational Question | `TRUE` | Structured conceptual explanation |
| 10 | `(25 + 15) * 2` | Calculation | `TRUE` | Evaluated to `80` |

---

## Project Structure

```
Minor Project new/
├── backend/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── classifier_agent.py      # Agent 1: Input Classifier
│   │   ├── calculator_agent.py      # Agent 2: Symbolic Calculator
│   │   ├── research_agent.py        # Agent 3: Research & Evidence Aggregator
│   │   ├── verifier_agent.py        # Agent 4: Fact Verifier
│   │   ├── validator_agent.py       # Agent 5: Evidence Validator
│   │   └── answer_agent.py          # Agent 6: Informational Answer Agent
│   ├── core/
│   │   ├── __init__.py
│   │   ├── models.py                # Pydantic data schemas
│   │   ├── orchestrator.py          # Multi-Agent pipeline orchestrator
│   │   └── source_ranker.py         # Domain reputation & credibility tiering
│   ├── data/
│   │   └── benchmark_facts.json     # Ground truth benchmark database
│   ├── api.py                       # FastAPI application & REST endpoints
│   └── config.py                    # Environment & configuration settings
├── frontend/
│   ├── index.html                   # Professional research portal UI
│   ├── style.css                    # Academic / journalistic styling
│   └── app.js                       # Client-side state & API communication
├── tests/
│   ├── __init__.py
│   └── test_agents.py               # 10 automated test cases (pytest)
├── .env.example
├── .env
├── requirements.txt
├── run.py                           # Single-command application launcher
└── README.md
```

---

## Quickstart & Installation

### 1. Prerequisites
- Python 3.9+ installed on your system.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Automated Tests
```bash
python -m pytest tests/test_agents.py -v
```
*(All 10 test cases should pass with 100% success).*

### 4. Launch the Application
```bash
python run.py
```

### 5. Access in Browser
- **Web Interface**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Interactive OpenAPI Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Viva & Project Defense FAQ

**Q1: Why did you design a multi-agent architecture instead of a single LLM prompt?**
> A single LLM prompt suffers from hallucination, confirmation bias (blindly agreeing with user assertions), and inaccurate arithmetic. By decoupling into specialized agents (Classification $\rightarrow$ Symbolic Calculator $\rightarrow$ Evidence Retrieval $\rightarrow$ Fact Verification $\rightarrow$ Evidence Validator), every decision is independently audited and backed by verifiable citations.

**Q2: How does the system prevent confirmation bias when a user submits "2 + 2 = 5 true"?**
> The Input Classifier Agent automatically strips leading and trailing bias tokens (`"true"`, `"false"`, `"verify this"`, `"is this correct"`). The raw claim `2 + 2 = 5` is sent to the Calculation Agent, which independently calculates the left-hand side (`4`), compares it against the proposed right-hand side (`5`), and strictly outputs `FALSE` with the correct statement `2 + 2 = 4`.

**Q3: How are source credibility scores calculated?**
> The `source_ranker` inspects the domain and URL pattern against institutional registers. Top tiers are assigned to `.gov` (Government), `.edu` / scientific research databases (Academic), NASA/WHO (Scientific), and peer-reviewed reference platforms before general web results.
