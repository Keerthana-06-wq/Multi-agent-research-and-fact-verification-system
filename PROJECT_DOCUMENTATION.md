# Veritas: Multi-Agent Research and Fact Verification System
## Comprehensive Technical Project Documentation & Viva Report

---

### Project Metadata
- **Project Title**: Multi-Agent Research and Fact Verification System (VERITAS)
- **Repository**: [Keerthana-06-wq/Multi-agent-research-and-fact-verification-system](https://github.com/Keerthana-06-wq/Multi-agent-research-and-fact-verification-system)
- **Architecture**: Decoupled Multi-Agent System (MAS) + Hybrid Symbolic-Neural Engine
- **Core Operating Principle**: *"Verify First, Answer Second"*
- **Target Domains**: Mathematics, Physical Sciences, Geography, History, Biological Sciences, Comparative Statements, Compound Propositions, Everyday Real-World Facts.

---

## Table of Contents
1. [Executive Summary](#1-executive-summary)
2. [Problem Statement & Motivation](#2-problem-statement--motivation)
3. [The Core Philosophy: "Verify First, Answer Second"](#3-the-core-philosophy-verify-first-answer-second)
4. [System Architecture & Data Flow](#4-system-architecture--data-flow)
5. [Specialized Multi-Agent Breakdown](#5-specialized-multi-agent-breakdown)
6. [Mathematical, Algorithmic & NLI Foundations](#6-mathematical-algorithmic--nli-foundations)
7. [Source Credibility & Evidence Ranking](#7-source-credibility--evidence-ranking)
8. [Frontend Research Workbench Design](#8-frontend-research-workbench-design)
9. [Experimental Evaluation & 18-Test Benchmark](#9-experimental-evaluation--18-test-benchmark)
10. [REST API Specification](#10-rest-api-specification)
11. [Deployment Architecture (Render & Vercel)](#11-deployment-architecture-render--vercel)
12. [Project Viva Voce & Defense Q&A](#12-project-viva-voce--defense-qa)

---

## 1. Executive Summary

**Veritas** is an advanced, production-grade Multi-Agent Fact Verification and Research System built to solve one of the most critical vulnerabilities in modern AI: **hallucination, sycophancy, and unverified assertion**.

Unlike monolithic Large Language Models (LLMs) that generate plausibly sounding text by predicting the next token, Veritas operates as a cooperative network of specialized, autonomous agents. Each incoming statement is classified, parsed for adversarial hints, decomposed into fundamental propositions, cross-referenced across authoritative institutional databases (Wikipedia, live DuckDuckGo web search, curated ground-truth datasets), mathematically computed via symbolic computer algebra (SymPy), and evaluated via **DeBERTa-v3 Natural Language Inference (NLI)** before any answer is formulated.

---

## 2. Problem Statement & Motivation

### The Pitfalls of Modern Generative AI:
1. **Hallucination**: LLMs confidently invent non-existent citations, historical dates, and scientific mechanisms.
2. **Sycophancy & Confirmation Bias**: When a user asks *"2 + 2 = 5 is true, right?"*, naive LLMs often agree with the user's premise rather than refuting it.
3. **Arithmetic Incompetence**: Standard generative models frequently fail multi-step arithmetic, percentage calculations, and inequality checks.
4. **Negation & Universal Blindness**: Standard keyword matching fails on negative claims (e.g., classifying *"Fish do not live on land"* as FALSE because it matches words "fish" and "land", or failing to disprove *"All birds can fly"* through flightless counterexamples like penguins).
5. **Black-Box Opacity**: Users are presented with assertions without traceable evidence chains, credibility metrics, or audit steps.

### The Veritas Solution:
Veritas enforces a transparent, multi-layered verification pipeline where claims are strictly evaluated against verifiable evidence, propositions are inverted algebraically for negative claims, and unproven statements default explicitly to **`UNVERIFIED`** rather than guessing.

---

## 3. The Core Philosophy: "Verify First, Answer Second"

The system enforces strict operational tenets:
1. **Never Guess**: If evidence is insufficient, contradictory, or absent, the verdict MUST be `UNVERIFIED`.
2. **Strip Adversarial Hints**: Suffixes and prefixes such as `"true"`, `"false"`, `"is it correct that..."` are cleanly extracted and stripped. The truth value of a claim is determined objectively, not by what the user suggests.
3. **Symbolic Computation for Math**: Math claims are computed deterministically through Python Abstract Syntax Trees (AST) and SymPy, guaranteeing 100% precision without probabilistic sampling.
4. **Proposition Inversion for Negations**:
   - A negative statement $S = \neg P$ is **TRUE** if and only if the underlying affirmative proposition $P$ is **FALSE**.
   - Example: *"The Sun does not rise in the west"* $\rightarrow$ Proposition: *"The Sun rises in the west"* is **FALSE** $\rightarrow$ Negative claim is **TRUE**.
5. **Universal Quantifier Counterexamples**: Words like *ALL*, *EVERY*, *ALWAYS*, *NEVER* demand universal validity; a single counterexample (e.g., penguins for flight) falsifies the universal statement.
6. **Traceability & Evidence First**: Every verdict is substantiated by ranked citations from accredited institutional domains.

---

## 4. System Architecture & Data Flow

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
               │                            │ (Splits into Sub-Claims)   │
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
               │                   │ (Premise-Hypothesis Entailment/Contra)    │
               │                   └─────────────────────┬─────────────────────┘
               │                                         │
               │                                         ▼
               │                   ┌───────────────────────────────────────────┐
               │                   │ Step 16: Fact Verifier Agent              │
               │                   │ (Assigns Initial Verdict & Confidence)    │
               │                   └─────────────────────┬─────────────────────┘
               │                                         │
               │                                         ▼
               │                   ┌───────────────────────────────────────────┐
               │                   │ Step 17: Evidence Validator Agent         │
               │                   │ (Audits Source Thresholds & Calibrates)   │
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

## 5. Specialized Multi-Agent Breakdown

The Veritas architecture is composed of 10 coordinated agent modules located in `backend/agents/`:

### 1. Input Classifier Agent (`classifier_agent.py`)
- **Role**: Categorizes the raw input into 15 semantic domains: `Mathematical`, `Scientific`, `Historical`, `Geographical`, `Social`, `Political`, `Technological`, `Environmental`, `Medical`, `General Knowledge`, `Real-life`, `Current Event`, `Comparison`, `Logical`, or `Mixed`.
- **Adversarial Suffix Stripper**: Detects and extracts trailing or leading assertions (`"true"`, `"false"`, `"correct"`, `"wrong"`, `"is it true that"`) so that the downstream agents evaluate only the core factual proposition.
- **Multiple Claims Separator**: Detects coordinating conjunctions (`" and "`, `" but "`) to decompose compound sentences into independent sub-claims.

### 2. Calculation Agent (`calculator_agent.py`)
- **Role**: Independent, deterministic arithmetic verification.
- **Methodology**: Parses the mathematical statement into an Abstract Syntax Tree (AST), identifies Left-Hand Side (LHS) and Right-Hand Side (RHS), and evaluates both sides using `sympy.sympify` and Python's `math` engine.
- **Capabilities**:
  - Exact equalities (`2 + 2 = 4` $\rightarrow$ TRUE, `2 + 2 = 5` $\rightarrow$ FALSE).
  - Multi-operand expressions (`10 × 5 = 50`, `12 * 12 = 144`).
  - Inequality statements (`100 is less than 20` $\rightarrow$ FALSE).
  - Percentage operations (`25% of 200 is 50` $\rightarrow$ TRUE).
- **Correction Generation**: When an equation is false, the calculator automatically computes the true RHS and generates the accurate equation (e.g. `2 + 2 = 4`).

### 3. Research Agent (`research_agent.py`)
- **Role**: Gathers corroborating and contradicting evidence from authoritative external repositories.
- **Channels**:
  - **Wikipedia API**: Legitimate User-Agent header integration (`VeritasFactChecker/2.0`) to avoid HTTP 403 blocks. Extracts page summaries and splits them into clean, verifiable factual sentences.
  - **Live Web (DuckDuckGo `ddgs`)**: Real-time multi-query web searching for time-sensitive, contemporary, or niche claims.
  - **Authoritative Ground-Truth Benchmark Database (`benchmark_facts.json`)**: Pre-validated institutional knowledge base containing peer-reviewed scientific and historical records.

### 4. Claim Normalizer Agent (`normalizer_agent.py`)
- **Role**: Cleans and standardizes raw user text by stripping redundant punctuation, extra whitespace, quotation marks, and normalizing capitalization for consistent linguistic analysis.

### 5. Negation Detector Agent (`negation_agent.py`)
- **Role**: Deep linguistic polarity analyzer.
- **Methodology**: Identifies explicit negative tokens: `"not"`, `"never"`, `"does not"`, `"cannot"`, `"without"`, `"no"`, `"neither"`, `"nowhere"`.
- **Proposition Extraction**: Generates the underlying affirmative counterpart.  
  *Example*: `"Water does not contain oxygen"` $\rightarrow$ Polarity: `NEGATIVE`, Proposition: `"Water contains oxygen"`.

### 6. Semantic NLI & Reasoning Agent (`semantic_nli_agent.py`)
- **Role**: The core cognitive inference engine.
- **Neural Component**: Integrates the local **`cross-encoder/nli-deberta-v3-xsmall`** transformer model. Evaluates `(premise, hypothesis)` pairs across all retrieved evidence sentences to compute softmax probabilities:
  $$\text{Softmax}(z) = \left[ P(\text{Contradiction}), P(\text{Entailment}), P(\text{Neutral}) \right]$$
- **Heuristic & Domain Rules**:
  - **Universal Quantifiers**: Evaluates claims with *all*, *every*, *always*.
  - **Comparative Logic**: Evaluates geographic and metric comparisons (e.g., surface areas of oceans).
  - **Thermodynamic Phase Transitions**: Evaluates state transitions (e.g., freezing liquid water yields ice).

### 7. Fact Verifier Agent (`verifier_agent.py`)
- **Role**: Synthesizes the NLI relation, research evidence, and proposition polarity into an initial verdict (`TRUE`, `FALSE`, `PARTIALLY TRUE`, or `UNVERIFIED`).
- **Narrative Explanation**: Constructs a concise, evidence-backed narrative explaining *why* the claim holds or fails.
- **Correction Statement**: Extracts the true counter-statement when a claim is FALSE.

### 8. Evidence Validator Agent (`validator_agent.py`)
- **Role**: Pre-presentation auditor and confidence calibrator.
- **Rules Enforced**:
  - A claim cannot be marked `TRUE` if there are 0 reliable sources or 0 evidence items.
  - Caps confidence at 35% for `UNVERIFIED` claims.
  - Downgrades confidence if source credibility falls below acceptable thresholds.

### 9. Verification Guard Agent (`guard_agent.py`)
- **Role**: Final quality and logical consistency enforcer (Step 18).
- **Enforcement**:
  - A negative statement is TRUE if the underlying affirmative proposition is contradicted by facts.
  - Prevents hallucinated confidence and enforces mandatory correction strings on all FALSE verdicts.

### 10. Answer Agent (`answer_agent.py`)
- **Role**: Formats clean, user-facing summaries and structures multi-claim responses.

---

## 6. Mathematical, Algorithmic & NLI Foundations

### 1. Mathematical Verification Formula
Given an equation string $E$:
1. Split $E$ at the relational operator ($=, \ne, <, >, \le, \ge$) into Left Expression $L$ and Right Expression $R$.
2. Parse $L$ and $R$ into symbolic expressions via SymPy:
   $$V_L = \text{sympify}(L), \quad V_R = \text{sympify}(R)$$
3. If operator is $=$, evaluate boolean condition $B = (V_L == V_R)$.
4. If $B = \text{False}$, the corrected equation is generated:
   $$E_{\text{correct}} = L \cup \{ = \} \cup \{ V_L \}$$

### 2. Natural Language Inference (NLI) Truth Determination
Let $H$ be the claim (hypothesis) and $E = \{e_1, e_2, \dots, e_k\}$ be the set of authoritative evidence sentences (premises).
For each pair $(e_i, H)$, DeBERTa-v3 computes:
$$\mathbf{p}_i = \left( p_{i, \text{contra}}, p_{i, \text{entail}}, p_{i, \text{neut}} \right)$$

The decision threshold $\tau = 0.70$ is applied:
$$\text{Verdict} = \begin{cases}
\text{FALSE}, & \text{if } \max_i(p_{i, \text{contra}}) \ge \tau \text{ and } \max_i(p_{i, \text{contra}}) > \max_i(p_{i, \text{entail}}) \\
\text{TRUE}, & \text{if } \max_i(p_{i, \text{entail}}) \ge \tau \\
\text{UNVERIFIED}, & \text{otherwise}
\end{cases}$$

### 3. Proposition Inversion Truth Table for Negations
| Affirmative Proposition $P$ | Evidence Status of $P$ | Negative Statement $S = \neg P$ | Final Verdict |
| :--- | :--- | :--- | :--- |
| "Water contains oxygen" | Confirmed TRUE | "Water does not contain oxygen" | **FALSE** |
| "The Sun rises in the west" | Refuted FALSE | "The Sun does not rise in the west" | **TRUE** |
| "Fish live on land" | Refuted FALSE | "Fish do not live on land" | **TRUE** |
| "India is in Europe" | Refuted FALSE | "India is not in Europe" | **TRUE** |
| "India is in Asia" | Confirmed TRUE | "India is not in Asia" | **FALSE** |

---

## 7. Source Credibility & Evidence Ranking

Every retrieved source citation is audited and categorized into one of six institutional credibility tiers via `backend/core/source_ranker.py`:

| Tier Level | Category Name | Domain Indicators | Base Credibility Score |
| :--- | :--- | :--- | :--- |
| **Tier 1** | **Government** | `.gov`, `.gov.in`, `.nic.in`, `.gov.uk`, `.europa.eu` | **95% – 100%** |
| **Tier 2** | **Academic & Research** | `.edu`, `.ac.in`, `.ac.uk`, `arxiv.org`, `jstor.org`, `nature.com` | **90% – 95%** |
| **Tier 3** | **Scientific Institutions** | `nasa.gov`, `who.int`, `cern.ch`, `isro.gov.in`, `nih.gov`, `usgs.gov` | **95% – 98%** |
| **Tier 4** | **Encyclopedic Reference** | `wikipedia.org`, `britannica.com`, `oxfordreference.com` | **85% – 90%** |
| **Tier 5** | **Reputable News Agencies** | `reuters.com`, `apnews.com`, `bbc.com`, `thehindu.com`, `nytimes.com` | **80% – 85%** |
| **Tier 6** | **General Web** | Other indexed web publications | **50% – 65%** |

---

## 8. Frontend Research Workbench Design

The frontend is intentionally designed as an **Editorial Two-Column Research Workbench**:
- **Canvas & Surface Palette**: Warm ivory and parchment tones (`#f6f4ee` canvas, `#fcfbf7` card surfaces, `#29241e` editorial serif + sans typography) replacing standard cold blue or dark tech themes.
- **Left Column (The Verification Deck)**:
  - Statement Input Bar with clear button and keyboard shortcuts (`Enter` to verify).
  - One-Click Preset Benchmark Pills categorized by domain.
  - Live Result Card featuring:
    - Organic mineral status badge (`TRUE` in Forest Olive, `FALSE` in Terracotta Crimson, `UNVERIFIED` in Warm Stone).
    - Calibrated Confidence Bar (0–100%).
    - Factual Explanation paragraph.
    - Highlighted Correction Box (for FALSE claims).
    - Compound Sub-claims breakout (for joined claims).
  - **12-Point Multi-Agent Quality Checklist**: Real-time visual confirmation of adversarial checks, negation handling, quantifier evaluation, AST computation, and source validation.
- **Right Column (The Evidence Inspector & History)**:
  - **Source Inspector**: Displays active citation cards with domain name, institutional credibility tier badge, credibility percentage, and excerpted snippet.
  - **Persistent History Deck**: Uses browser `localStorage` to save all verified claims; clicking any past claim instantly reloads its verification card and sources.

---

## 9. Experimental Evaluation & 18-Test Benchmark

The test suite in `tests/test_agents.py` rigorously validates the system against 18 comprehensive test scenarios:

| # | Test Query | Domain / Logic | Expected Verdict | Actual Result | Verification Mechanism |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | `India became independent in 1947 true` | Adversarial Suffix | **TRUE** | **TRUE** | Strips suggested `"true"`, validates historical record via Wikipedia. |
| **2** | `2 + 2 = 5 false` | Math + Adversarial | **FALSE** | **FALSE** | Strips `"false"`, computes AST $4 \ne 5$, generates correction `2 + 2 = 4`. |
| **3** | `Water does not contain oxygen.` | Scientific Negation | **FALSE** | **FALSE** | Proposition $H_2O$ contains O is true $\rightarrow$ negation is FALSE. |
| **4** | `The Sun does not rise in the west.` | Planetary Negation | **TRUE** | **TRUE** | Proposition (rises in west) is false $\rightarrow$ negative statement is TRUE. |
| **5** | `India is not in Europe.` | Geographic Negation | **TRUE** | **TRUE** | Proposition (in Europe) is false $\rightarrow$ negative statement is TRUE. |
| **6** | `India is not in Asia.` | Geographic Negation | **FALSE** | **FALSE** | Proposition (in Asia) is true $\rightarrow$ negative statement is FALSE. |
| **7** | `Humans cannot breathe underwater without equipment.` | Biological Law | **TRUE** | **TRUE** | Validates pulmonary respiration requirement. |
| **8** | `2 + 2 = 4` | Arithmetic Equality | **TRUE** | **TRUE** | SymPy evaluates $2 + 2 == 4 \rightarrow \text{True}$. |
| **9** | `10 × 5 = 50` | Arithmetic Multiply | **TRUE** | **TRUE** | SymPy evaluates $10 \times 5 == 50 \rightarrow \text{True}$. |
| **10** | `100 is less than 20` | Inequality Comparison | **FALSE** | **FALSE** | Computes $100 < 20 \rightarrow \text{False}$. Corrects to $100 > 20$. |
| **11** | `25% of 200 is 50` | Percentage Arithmetic | **TRUE** | **TRUE** | Computes $0.25 \times 200 == 50 \rightarrow \text{True}$. |
| **12** | `All birds can fly.` | Universal Quantifier | **FALSE** | **FALSE** | Counterexamples identified (penguins, ostriches, emus). |
| **13** | `The Pacific Ocean is larger than the Atlantic Ocean.` | Geographic Comparison | **TRUE** | **TRUE** | Surface area comparison ($165\text{M km}^2 > 106\text{M km}^2$). |
| **14** | `The Atlantic Ocean is larger than the Pacific Ocean.` | Geographic Comparison | **FALSE** | **FALSE** | Comparison contradiction detected. |
| **15** | `India became independent in 1947 and Mumbai is the capital of India.` | Multiple Claims | **FALSE** | **FALSE** | Claim 1 is TRUE, Claim 2 is FALSE $\rightarrow$ Overall statement is FALSE. |
| **16** | `Fish do not live in water.` | Biological Negation | **FALSE** | **FALSE** | Aquatic habitat proposition is true $\rightarrow$ negative claim is FALSE. |
| **17** | `Fish do not live on land.` | Biological Negation | **TRUE** | **TRUE** | Terrestrial habitat proposition is false $\rightarrow$ negative claim is TRUE. |
| **18** | `freezing of water will not turns into ice` | Physical Law | **FALSE** | **FALSE** | Thermodynamic phase transition at $0^\circ\text{C}$ contradicts claim. |

---

## 10. REST API Specification

The backend provides high-performance asynchronous REST endpoints:

### 1. `POST /api/verify`
Evaluates any claim through the 18-step verification pipeline.
- **Request Body**:
```json
{
  "query": "Humans have two eyes"
}
```
- **Response Payload**:
```json
{
  "claim": "Humans have two eyes",
  "category": "Real-life",
  "verdict": "TRUE",
  "confidence": 77,
  "explanation": "The claim is true. Authoritative evidence confirms this claim: \"In visual science, binocular vision focuses on visual perception with two eyes instead of one.\" Reliable research evidence directly substantiates this statement.",
  "evidence": [
    "In visual science, binocular vision focuses on visual perception with two eyes instead of one."
  ],
  "sources": [
    {
      "title": "Wikipedia: Binocular vision",
      "url": "https://en.wikipedia.org/wiki/Binocular_vision",
      "domain": "en.wikipedia.org",
      "snippet": "Binocular vision is a type of vision in which an animal has two eyes capable of facing the same direction...",
      "tier": "Reference / Encyclopedia",
      "credibility_score": 88
    }
  ],
  "correct_statement": null,
  "sub_claims": null,
  "quality_checks": {
    "extracted_correct_claim": true,
    "ignored_suggested_answer": false,
    "understood_complete_sentence": true,
    "handled_negation": false,
    "handled_universal_quantifiers": false,
    "verified_numbers_dates": false,
    "verified_comparisons": false,
    "separated_multiple_claims": false,
    "reasoning_before_search": false,
    "reliable_evidence_used": true,
    "unverified_rule_respected": true
  },
  "agent_traces": [
    {
      "agent_name": "Step 1 & 3: Claim Extraction & Classification",
      "status": "COMPLETED",
      "summary": "Categorized as Real-life",
      "details": "Extracted Claim: 'Humans have two eyes'. Stripped suggested hint: False."
    },
    {
      "agent_name": "Step 13: Research Agent",
      "status": "COMPLETED",
      "summary": "Gathered 4 authoritative citations",
      "details": "Gathered evidence from institutional sources, Wikipedia, and verified benchmarks."
    },
    {
      "agent_name": "Step 10 & 11: Semantic NLI & Reasoning",
      "status": "COMPLETED",
      "summary": "Relation: ENTAILMENT",
      "details": "Authoritative evidence confirms this claim."
    },
    {
      "agent_name": "Step 18: Verification Guard & Quality Check",
      "status": "COMPLETED",
      "summary": "Final Verdict Confirmed: TRUE",
      "details": "Ensured logical consistency between evidence, negation, and verdict."
    }
  ]
}
```

### 2. `GET /api/preset-cases`
Returns the curated list of benchmark demo cases to populate the UI pills.

### 3. `GET /health`
Returns system status (`{"status": "ok", "system": "Veritas 18-Step Advanced Fact Verification Agent"}`).

### 4. `GET /docs`
Interactive Swagger OpenAPI documentation.

---

## 11. Deployment Architecture (Render & Vercel)

### Production Deployment on Render (Active)
- **Start Command**: `uvicorn backend.api:app --host 0.0.0.0 --port $PORT`
- **Build Command**: `pip install -r requirements.txt`
- **Infrastructure File (`render.yaml`)**:
```yaml
services:
  - type: web
    name: veritas-fact-verification
    runtime: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn backend.api:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.10.12
```

### Serverless Deployment on Vercel
- **Bridge File (`api/index.py`)**: Exposes FastAPI ASGI app to Vercel Serverless.
- **Routing Configuration (`vercel.json`)**: Configured to statically serve `/frontend` and forward `/api/*` requests to the Python serverless runtime.

---

## 12. Project Viva Voce & Defense Q&A

Here are the top technical questions frequently asked by project examiners along with ideal answers:

### Q1: What makes Veritas different from ChatGPT or other LLMs?
> **Answer**: Standard LLMs generate responses probabilistically without verifying facts, leading to hallucinations and sycophancy (agreeing with false user premises). Veritas is a **decoupled Multi-Agent System** that separates fact verification into explicit, deterministic sub-tasks. It calculates math through computer algebra (SymPy), retrieves live citations from accredited institutional sources, tests entailment via DeBERTa-v3 Natural Language Inference, and defaults to `UNVERIFIED` if evidence is missing.

### Q2: How does the system handle negative statements like "Water does not contain oxygen"?
> **Answer**: Standard keyword matching fails because words like "water" and "oxygen" co-occur frequently. Veritas uses a **Negation Analyzer** that identifies the negative polarity, extracts the affirmative proposition (*"Water contains oxygen"*), searches for evidence on the proposition, and applies the logic: if the affirmative proposition is verified as TRUE, the negative claim is conclusively marked **FALSE**.

### Q3: Why use DeBERTa-v3 NLI instead of simple string search or cosine similarity?
> **Answer**: Cosine similarity between text embeddings only measures topical similarity, not truth value. For example, *"The Earth is flat"* and *"The Earth is round"* have a cosine similarity above 0.85 because they discuss the same topic. Natural Language Inference (NLI) with DeBERTa-v3 explicitly classifies the semantic relation into **Entailment**, **Contradiction**, or **Neutral**, allowing the system to identify factual contradictions accurately.

### Q4: What happens if an adversarial user enters "2 + 2 = 5 true"?
> **Answer**: In Step 1, the **Input Classifier Agent** runs an adversarial hint stripper that identifies leading/trailing bias tokens like `"true"`, `"false"`, or `"correct"`. It isolates the core claim `"2 + 2 = 5"`, hands it to the **Calculation Agent**, evaluates $4 \ne 5$, marks the verdict as **FALSE**, and generates the correct statement `"2 + 2 = 4"`.

### Q5: What is the fallback if an obscure or unproven claim is submitted (e.g. "Aliens built the pyramids")?
> **Answer**: In accordance with the *"Verify First, Answer Second"* principle and our Evidence Validator rules, if retrieved sources lack accredited consensus or provide no peer-reviewed documentation, the system strictly assigns the verdict **`UNVERIFIED`** with a low confidence score (e.g. 20-30%) and explains that reliable evidence is insufficient, preventing false assertions.

---

### Conclusion
Veritas demonstrates that transparent, multi-agent systems with explicit verification pipelines provide a reliable, hallucination-resistant alternative to black-box generative AI for academic research, journalistic fact-checking, and educational fact verification.
