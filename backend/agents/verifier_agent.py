import logging
from typing import Dict, Any, List, Optional
from backend.core.models import FactVerdict, SourceItem, PartiallyTrueDetails
from backend.agents.semantic_nli_agent import NLIRelation

logger = logging.getLogger(__name__)

class FactVerifierAgent:
    """
    Agent 7: Fact Verification Agent
    Independently evaluates the claim against the gathered research evidence using semantic NLI.
    Strictly follows 'VERIFY FIRST, ANSWER SECOND'.
    Never assumes a claim is true or false without direct evidence alignment.
    """

    def verify(
        self,
        normalized_claim: str,
        claim_analysis: Dict[str, Any],
        research_data: Dict[str, Any],
        nli_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        benchmark = research_data.get("benchmark_match")
        sources: List[SourceItem] = research_data.get("sources", [])
        evidence_list: List[str] = research_data.get("evidence", [])
        has_negation = claim_analysis.get("has_negation", False)

        # 1. Authoritative Benchmark Check (handles PARTIALLY TRUE or exact ground-truth)
        if benchmark:
            if "verdict" in benchmark:
                v_str = benchmark["verdict"]
                verdict = FactVerdict(v_str) if v_str in [v.value for v in FactVerdict] else FactVerdict.PARTIALLY_TRUE
                pt_data = benchmark.get("partially_true_details")
                pt_obj = PartiallyTrueDetails(**pt_data) if pt_data else None
                return {
                    "verdict": verdict,
                    "confidence": 96,
                    "correct_statement": pt_data.get("accurate_statement") if pt_data else None,
                    "partially_true_details": pt_obj,
                    "explanation": benchmark.get("explanation", ""),
                    "evidence": evidence_list,
                    "sources": sources
                }

        # 2. Semantic NLI Mapping
        relation = nli_result.get("relation", NLIRelation.UNKNOWN)
        confidence = nli_result.get("confidence", 50)
        nli_reasoning = nli_result.get("reasoning", "")
        correct_stmt = nli_result.get("correct_statement")

        if relation == NLIRelation.CONTRADICTION:
            verdict = FactVerdict.FALSE
            if not correct_stmt:
                correct_stmt = claim_analysis.get("positive_proposition", "").capitalize()
            explanation = (
                f"The claim is false. {nli_reasoning} "
                f"The evidence directly contradicts the stated proposition."
            )
            return {
                "verdict": verdict,
                "confidence": confidence,
                "correct_statement": correct_stmt,
                "partially_true_details": None,
                "explanation": explanation,
                "evidence": evidence_list,
                "sources": sources
            }

        elif relation == NLIRelation.ENTAILMENT:
            verdict = FactVerdict.TRUE
            explanation = (
                f"The claim is true. {nli_reasoning} "
                f"Reliable research evidence directly substantiates this statement."
            )
            return {
                "verdict": verdict,
                "confidence": confidence,
                "correct_statement": None,
                "partially_true_details": None,
                "explanation": explanation,
                "evidence": evidence_list,
                "sources": sources
            }

        else: # UNKNOWN / Insufficient
            return {
                "verdict": FactVerdict.UNVERIFIED,
                "confidence": min(confidence, 35),
                "correct_statement": None,
                "partially_true_details": None,
                "explanation": "There is not enough reliable evidence available from authoritative sources to confirm or reject this statement.",
                "evidence": evidence_list if evidence_list else ["No conclusive historical, scientific, or academic documentation available."],
                "sources": sources
            }
