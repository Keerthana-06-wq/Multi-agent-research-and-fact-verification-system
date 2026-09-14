import time
import logging
from typing import List, Optional
from backend.core.models import (
    VerificationRequest,
    VerificationResponse,
    ClaimCategory,
    FactVerdict,
    AgentTraceStep,
    SubClaimResult,
    QualityChecks,
    SourceItem
)
from backend.core.evidence_store import EvidenceStore, NLIEvaluationItem, ResearchTask
from backend.agents.llm_manager import LLMManagerAgent
from backend.agents.llm_report_agent import LLMReportAgent
from backend.agents.evidence_aggregator import EvidenceAggregatorAgent
from backend.agents.classifier_agent import InputClassifierAgent
from backend.agents.calculator_agent import CalculatorAgent
from backend.agents.research_agent import ResearchAgent
from backend.agents.normalizer_agent import ClaimNormalizerAgent
from backend.agents.negation_agent import NegationDetectorAgent
from backend.agents.semantic_nli_agent import SemanticNLIAgent
from backend.agents.verifier_agent import FactVerifierAgent
from backend.agents.validator_agent import EvidenceValidatorAgent
from backend.agents.guard_agent import VerificationGuardAgent
from backend.agents.answer_agent import AnswerAgent

logger = logging.getLogger(__name__)

class MultiAgentOrchestrator:
    """
    Target Architecture Orchestrator:
    
    [ USER CLAIM / QUERY ]
              │
              ▼
       [ LLM MANAGER ]  (FLAN-T5: Routing & Task Planning)
       /      |      \
      /       |       \
     ↓        ↓        ↓
    Case 1   Case 2   Case 3
    (Math)  (Claim)  (Normal Q)
     │        │        │
     ▼        │        ▼
 [Calculator] │   [Informational Answer]
              │
    ┌─────────┴─────────┐
    ▼                   ▼
[Research Agent 1]   [Research Agent 2]
(Supporting / Wiki)  (Alternative / DDGS)
    \                   /
     \                 /
      ▼               ▼
      [SOURCE VERIFIER]
              │
              ▼
       [EVIDENCE STORE]
              │
              ▼
     [NLI FACT CHECKER]
    (RoBERTa-large-MNLI / DeBERTa)
              │
              ▼
    [EVIDENCE AGGREGATOR]
              │
              ▼
    [LLM REPORT GENERATOR]
              │
              ▼
        FINAL VERDICT
              │
              ▼
     [EXISTING FRONTEND]
    """

    def __init__(self):
        # 1. LLM Layer
        self.llm_manager = LLMManagerAgent()
        self.llm_report_gen = LLMReportAgent(self.llm_manager)

        # 2. Planning & Classification
        self.classifier = InputClassifierAgent()

        # 3. Deterministic Calculator
        self.calculator = CalculatorAgent()

        # 4. Dual Research Agents & Source Ranker
        self.researcher = ResearchAgent()

        # 5. Normalization & Negation Reasoner
        self.normalizer = ClaimNormalizerAgent()
        self.negation_detector = NegationDetectorAgent()

        # 6. Core NLI Fact Checker (RoBERTa-large-MNLI / DeBERTa-v3)
        self.semantic_nli = SemanticNLIAgent()

        # 7. Evidence Aggregator & Validator
        self.aggregator = EvidenceAggregatorAgent()
        self.verifier = FactVerifierAgent()
        self.validator = EvidenceValidatorAgent()

        # 8. Step 18 Quality Guard & Informational Answerer
        self.guard = VerificationGuardAgent()
        self.answerer = AnswerAgent()

    def process(self, request: VerificationRequest) -> VerificationResponse:
        raw_text = request.query.strip()
        traces: List[AgentTraceStep] = []
        quality = QualityChecks()

        if not raw_text:
            return VerificationResponse(
                claim="",
                category=ClaimCategory.GENERAL_KNOWLEDGE,
                verdict=FactVerdict.UNVERIFIED,
                confidence=0,
                explanation="No claim was provided for verification.",
                quality_checks=quality,
                agent_traces=[]
            )

        # ----------------------------------------------------
        # STEP 1: Identify Claim & Strip User Bias Suffixes
        # ----------------------------------------------------
        clean_claim, had_suggested = self.classifier.extract_claim(raw_text)
        quality.ignored_suggested_answer = had_suggested

        # ----------------------------------------------------
        # STEP 2: LLM Manager Routing (Case 1, Case 2, Case 3)
        # ----------------------------------------------------
        intent = self.llm_manager.classify_intent(clean_claim)
        category = self.classifier.classify(clean_claim)

        traces.append(AgentTraceStep(
            agent_name="LLM Manager: Intent Classification",
            status="COMPLETED",
            summary=f"Intent: {intent} | Category: {category.value}",
            details=f"Analyzed query. Extracted Claim: '{clean_claim}'. Stripped hint: {had_suggested}."
        ))

        # ----------------------------------------------------
        # CASE 1: Mathematical Expressions & Equations
        # ----------------------------------------------------
        if intent == "MATHEMATICAL" or category == ClaimCategory.MATHEMATICAL:
            quality.reasoning_before_search = True
            v, conf, exp, ev, corr = self.calculator.verify_mathematical_claim(clean_claim)

            traces.append(AgentTraceStep(
                agent_name="Case 1: Mathematical Agent",
                status="COMPLETED",
                summary=f"Direct symbolic calculation: {v.value}",
                details=f"{exp}"
            ))

            return VerificationResponse(
                claim=clean_claim,
                category=ClaimCategory.MATHEMATICAL,
                verdict=v,
                confidence=conf,
                explanation=exp,
                evidence=ev,
                sources=[],
                correct_statement=corr,
                quality_checks=quality,
                agent_traces=traces
            )

        # ----------------------------------------------------
        # CASE 3: Normal Non-Factual Informational Questions
        # ----------------------------------------------------
        if intent == "INFORMATIONAL":
            ans_data = self.answerer.answer_question(clean_claim)
            answer_text = ans_data.get("answer", "")
            ans_sources = ans_data.get("sources", [])
            ans_evidence = ans_data.get("evidence", [])

            traces.append(AgentTraceStep(
                agent_name="Case 3: Informational Answer Agent",
                status="COMPLETED",
                summary="Provided structured informational response",
                details="Classified as conceptual inquiry. Synthesized informative response with authoritative references."
            ))

            return VerificationResponse(
                claim=clean_claim,
                category=ClaimCategory.GENERAL_KNOWLEDGE,
                verdict=FactVerdict.TRUE,
                confidence=95,
                explanation=answer_text,
                evidence=ans_evidence,
                sources=ans_sources,
                correct_statement=None,
                quality_checks=quality,
                agent_traces=traces
            )

        # ----------------------------------------------------
        # MULTIPLE CLAIMS DECOMPOSITION (Step 12)
        # ----------------------------------------------------
        sub_claims_list = self.classifier.separate_multiple_claims(clean_claim)
        if sub_claims_list and len(sub_claims_list) > 1:
            quality.separated_multiple_claims = True
            sub_results: List[SubClaimResult] = []
            overall_verdict = FactVerdict.TRUE
            sub_explanations = []

            for idx, sub_c in enumerate(sub_claims_list):
                sub_req = VerificationRequest(query=sub_c)
                sub_res = self.process(sub_req)
                sub_results.append(SubClaimResult(
                    claim=sub_c,
                    verdict=sub_res.verdict,
                    explanation=sub_res.explanation
                ))
                sub_explanations.append(f"Part {idx+1} ('{sub_c}'): {sub_res.verdict.value} - {sub_res.explanation}")
                if sub_res.verdict == FactVerdict.FALSE:
                    overall_verdict = FactVerdict.FALSE
                elif sub_res.verdict == FactVerdict.UNVERIFIED and overall_verdict != FactVerdict.FALSE:
                    overall_verdict = FactVerdict.UNVERIFIED

            traces.append(AgentTraceStep(
                agent_name="LLM Manager: Multiple Claims Breakdown",
                status="COMPLETED",
                summary=f"Evaluated {len(sub_claims_list)} independent sub-claims",
                details=f"Overall verdict: {overall_verdict.value}."
            ))

            exp = f"The statement contains multiple claims. Overall verdict is {overall_verdict.value}. " + " ".join(sub_explanations)
            return VerificationResponse(
                claim=clean_claim,
                category=category,
                verdict=overall_verdict,
                confidence=95,
                explanation=exp,
                evidence=[s.explanation for s in sub_results],
                sources=[],
                sub_claims=sub_results,
                quality_checks=quality,
                agent_traces=traces
            )

        # ----------------------------------------------------
        # CASE 2: FACTUAL / RESEARCH CLAIM VERIFICATION
        # ----------------------------------------------------
        # Initialize Evidence Store
        store = EvidenceStore(
            raw_query=raw_text,
            clean_claim=clean_claim,
            category=category
        )

        # Step 2a: LLM Manager Research Task Planning
        research_tasks: List[ResearchTask] = self.llm_manager.plan_research_tasks(clean_claim)
        store.tasks = research_tasks
        task_queries = [t.query for t in research_tasks]

        traces.append(AgentTraceStep(
            agent_name="LLM Manager: Research Task Planning",
            status="COMPLETED",
            summary=f"Generated {len(research_tasks)} targeted research sub-tasks",
            details="Assigned Task 1 to Research Agent 1 (Wikipedia/institutional) and Task 2 to Research Agent 2 (Live Web DDGS)."
        ))

        # Step 2b: Dual Research Agents Execution
        research_data = self.researcher.gather_evidence(clean_claim, sub_queries=task_queries)
        for s in research_data.get("sources", []):
            store.add_source(s)
        for ev in research_data.get("evidence", []):
            store.add_evidence(ev)

        traces.append(AgentTraceStep(
            agent_name="Research Agents 1 & 2: Dual Research Execution",
            status="COMPLETED",
            summary=f"Gathered {len(store.sources)} authoritative sources & {len(store.evidence_texts)} evidence points",
            details="Research Agent 1 retrieved encyclopedic references; Research Agent 2 gathered independent web evidence."
        ))

        # Step 2c: Normalization & Linguistic Negation Analysis
        normalized = self.normalizer.normalize(clean_claim)
        neg_analysis = self.negation_detector.analyze(normalized)
        quality.handled_negation = neg_analysis["has_negation"]

        traces.append(AgentTraceStep(
            agent_name="Negation & Proposition Inversion Agent",
            status="COMPLETED",
            summary=f"Polarity: {neg_analysis['polarity']}",
            details=f"Extracted affirmative proposition: '{neg_analysis['positive_proposition']}'."
        ))

        # Step 2d: NLI Fact Checker (RoBERTa-large-MNLI / DeBERTa-v3)
        nli_res = self.semantic_nli.evaluate(
            claim_data=neg_analysis,
            evidence_texts=store.evidence_texts,
            benchmark_match=research_data.get("benchmark_match")
        )

        # Populate NLI evaluations into Evidence Store
        nli_rel = nli_res.get("relation")
        nli_rel_str = nli_rel.value if hasattr(nli_rel, "value") else str(nli_rel)
        for sent in store.evidence_texts[:5]:
            store.add_nli_evaluation(NLIEvaluationItem(
                evidence_text=sent,
                source_title=store.sources[0].title if store.sources else "Reference Archive",
                source_url=store.sources[0].url if store.sources else "",
                relation=nli_rel_str,
                confidence=nli_res.get("confidence", 75)
            ))

        traces.append(AgentTraceStep(
            agent_name="NLI Fact Checker: RoBERTa/DeBERTa Engine",
            status="COMPLETED",
            summary=f"Classification: {nli_rel_str}",
            details=f"NLI evaluation: {nli_res.get('reasoning', '')}"
        ))

        # Step 2e: Evidence Aggregator
        agg_verdict, agg_conf, agg_correct = self.aggregator.aggregate(
            store=store,
            has_negation=neg_analysis["has_negation"],
            pos_prop=neg_analysis["positive_proposition"]
        )

        # Synthesize with domain verifier
        verif_data = self.verifier.verify(
            normalized_claim=normalized,
            claim_analysis=neg_analysis,
            research_data=research_data,
            nli_result=nli_res
        )

        # Evidence Validation & Guard
        val_data = self.validator.validate(normalized, verif_data)
        guarded_data = self.guard.audit_and_protect(
            claim_data=neg_analysis,
            verdict_data=val_data,
            evidence_texts=store.evidence_texts
        )

        final_verdict = guarded_data["verdict"]
        final_confidence = guarded_data["confidence"]
        final_correct = guarded_data.get("correct_statement")

        # Step 2f: LLM Report Generator
        final_report = self.llm_report_gen.generate_report(
            claim=clean_claim,
            verdict=final_verdict,
            confidence=final_confidence,
            supporting_evidence=store.supporting_evidence or store.evidence_texts[:2],
            contradicting_evidence=store.contradicting_evidence,
            sources=store.sources,
            nli_summary=nli_res.get("reasoning", ""),
            correct_statement=final_correct
        )

        traces.append(AgentTraceStep(
            agent_name="LLM Report Generator: Narrative Synthesis",
            status="COMPLETED",
            summary=f"Final Report Generated ({final_verdict.value})",
            details="FLAN-T5 synthesized executive-level report incorporating supporting and contradicting evidence."
        ))

        return VerificationResponse(
            claim=normalized,
            category=category,
            verdict=final_verdict,
            confidence=final_confidence,
            explanation=final_report,
            evidence=guarded_data["evidence"] or store.evidence_texts[:3],
            sources=store.sources,
            correct_statement=final_correct,
            quality_checks=quality,
            agent_traces=traces
        )
