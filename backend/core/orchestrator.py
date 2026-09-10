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
    Executes the comprehensive 18-step verification pipeline:
    1. Identify Claim (strip suggested answers)
    2. Understand Complete Meaning (negation, universals)
    3. Classify Claim
    4. Mathematical Verification
    5-8. Science, Geography, History, Real-Life Verification
    9. Negative Statements Inversion
    10. Universal Words (All/Every)
    11. Comparisons
    12. Multiple Claims Separation
    13-15. Web Research & Current Info
    16. Strict Unverified Rule
    17. Calibrated Confidence
    18. Standardized Output Format
    """

    def __init__(self):
        self.classifier = InputClassifierAgent()
        self.calculator = CalculatorAgent()
        self.researcher = ResearchAgent()
        self.normalizer = ClaimNormalizerAgent()
        self.negation_detector = NegationDetectorAgent()
        self.semantic_nli = SemanticNLIAgent()
        self.verifier = FactVerifierAgent()
        self.validator = EvidenceValidatorAgent()
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
        # STEP 1: Identify Claim (Strip suggested true/false)
        # ----------------------------------------------------
        clean_claim, had_suggested = self.classifier.extract_claim(raw_text)
        quality.ignored_suggested_answer = had_suggested

        # ----------------------------------------------------
        # STEP 3: Classify Claim
        # ----------------------------------------------------
        category = self.classifier.classify(clean_claim)

        traces.append(AgentTraceStep(
            agent_name="Step 1 & 3: Claim Extraction & Classification",
            status="COMPLETED",
            summary=f"Categorized as {category.value}",
            details=f"Extracted Claim: '{clean_claim}'. Stripped suggested hint: {had_suggested}."
        ))

        # ----------------------------------------------------
        # STEP 12: Multiple Claims Separation (if joined by 'and')
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
                sub_explanations.append(f"Claim {idx+1} ('{sub_c}'): {sub_res.verdict.value} - {sub_res.explanation}")
                if sub_res.verdict == FactVerdict.FALSE:
                    overall_verdict = FactVerdict.FALSE
                elif sub_res.verdict == FactVerdict.UNVERIFIED and overall_verdict != FactVerdict.FALSE:
                    overall_verdict = FactVerdict.UNVERIFIED

            traces.append(AgentTraceStep(
                agent_name="Step 12: Multiple Claims Agent",
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
        # STEP 4: Mathematical Verification
        # ----------------------------------------------------
        if category == ClaimCategory.MATHEMATICAL:
            quality.reasoning_before_search = True
            v, conf, exp, ev, corr = self.calculator.verify_mathematical_claim(clean_claim)

            traces.append(AgentTraceStep(
                agent_name="Step 4: Mathematical Agent",
                status="COMPLETED",
                summary=f"Independently calculated verdict: {v.value}",
                details=f"{exp}"
            ))

            return VerificationResponse(
                claim=clean_claim,
                category=category,
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
        # STEPS 2, 5-11, 13-17: Comprehensive Semantic & Research Pipeline
        # ----------------------------------------------------
        # Step 13: Research Agent
        research_data = self.researcher.gather_evidence(clean_claim)
        traces.append(AgentTraceStep(
            agent_name="Step 13: Research Agent",
            status="COMPLETED",
            summary=f"Gathered {len(research_data['sources'])} authoritative citations",
            details="Gathered evidence from institutional sources, Wikipedia, and verified benchmarks."
        ))

        # Step 2: Normalization
        normalized = self.normalizer.normalize(clean_claim)

        # Step 9: Negation Detection & Proposition Inversion
        neg_analysis = self.negation_detector.analyze(normalized)
        quality.handled_negation = neg_analysis["has_negation"]

        traces.append(AgentTraceStep(
            agent_name="Step 9: Negation & Proposition Inversion",
            status="COMPLETED",
            summary=f"Polarity: {neg_analysis['polarity']}",
            details=f"Affirmative proposition: '{neg_analysis['positive_proposition']}'."
        ))

        # Steps 5, 6, 7, 8, 10, 11: Semantic NLI Evaluation
        nli_res = self.semantic_nli.evaluate(
            claim_data=neg_analysis,
            evidence_texts=research_data.get("evidence", []),
            benchmark_match=research_data.get("benchmark_match")
        )

        traces.append(AgentTraceStep(
            agent_name="Step 10 & 11: Semantic NLI & Reasoning",
            status="COMPLETED",
            summary=f"Relation: {nli_res['relation'].value}",
            details=f"Reasoning: {nli_res['reasoning']}"
        ))

        # Fact Verification
        verif_data = self.verifier.verify(
            normalized_claim=normalized,
            claim_analysis=neg_analysis,
            research_data=research_data,
            nli_result=nli_res
        )

        # Evidence Validation
        val_data = self.validator.validate(normalized, verif_data)

        # Verification Guard (Final Quality Check)
        guarded_data = self.guard.audit_and_protect(
            claim_data=neg_analysis,
            verdict_data=val_data,
            evidence_texts=research_data.get("evidence", [])
        )

        traces.append(AgentTraceStep(
            agent_name="Step 18: Verification Guard & Quality Check",
            status="COMPLETED",
            summary=f"Final Verdict Confirmed: {guarded_data['verdict'].value}",
            details="Ensured logical consistency between evidence, negation, and verdict."
        ))

        return VerificationResponse(
            claim=normalized,
            category=category,
            verdict=guarded_data["verdict"],
            confidence=guarded_data["confidence"],
            explanation=guarded_data["explanation"],
            evidence=guarded_data["evidence"],
            sources=guarded_data["sources"],
            correct_statement=guarded_data.get("correct_statement"),
            quality_checks=quality,
            agent_traces=traces
        )
