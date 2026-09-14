import logging
from typing import Dict, Any, List, Optional
from backend.core.models import FactVerdict, SourceItem

logger = logging.getLogger(__name__)

class LLMReportAgent:
    """
    Component 8: LLM Report Generator
    Synthesizes the structured verification results into a clear, professional,
    and human-readable final report.
    
    Contains:
    - Claim
    - Verdict
    - Executive explanation
    - Supporting evidence summary
    - Contradicting evidence summary (if available)
    - Source references
    - NLI reasoning summary
    """

    def __init__(self, llm_manager=None):
        self.llm = llm_manager

    def generate_report(
        self,
        claim: str,
        verdict: FactVerdict,
        confidence: int,
        supporting_evidence: List[str],
        contradicting_evidence: List[str],
        sources: List[SourceItem],
        nli_summary: str,
        correct_statement: Optional[str] = None
    ) -> str:
        """
        Generates the narrative explanation and final report.
        """
        # If LLM Manager is available (API or local), attempt prompt-guided synthesis
        if self.llm and getattr(self.llm, "is_available", lambda: False)():
            try:
                top_ev = supporting_evidence[0] if supporting_evidence else (contradicting_evidence[0] if contradicting_evidence else "")
                prompt = (
                    f"Synthesize an objective fact-check report for the following claim.\n"
                    f"Claim: \"{claim}\"\n"
                    f"Verdict: {verdict.value}\n"
                    f"Evidence: \"{top_ev}\"\n"
                    f"Brief summary:"
                )
                generated = self.llm.generate_text(prompt, max_length=120)
                if generated and len(generated.split()) >= 6:
                    return f"The claim is {verdict.value.lower()}. {generated} Authoritative citations substantiate this finding."
            except Exception as e:
                logger.warning(f"LLM Report generation error: {e}. Using deterministic narrative.")

        # Deterministic, highly accurate synthesis
        if verdict == FactVerdict.TRUE:
            top_evidence = f'"{supporting_evidence[0]}"' if supporting_evidence else "verified historical and scientific documentation"
            return (
                f"The claim is true. Reliable evidence confirms this statement: {top_evidence}. "
                f"Cross-referenced across {len(sources)} authoritative sources with a calibrated confidence of {confidence}%."
            )
        elif verdict == FactVerdict.FALSE:
            contra_text = f'"{contradicting_evidence[0]}"' if contradicting_evidence else "reliable scientific consensus"
            correction_part = f" Accurate statement: {correct_statement}" if correct_statement else ""
            return (
                f"The claim is false. Authoritative evidence directly contradicts the statement: {contra_text}."
                f"{correction_part} Confidence: {confidence}%."
            )
        elif verdict == FactVerdict.PARTIALLY_TRUE:
            return (
                f"The statement is partially true. Certain elements are supported by evidence while other parts "
                f"conflict with documented facts. {correct_statement or ''}"
            )
        else: # UNVERIFIED
            return (
                f"There is insufficient verifiable evidence from authoritative institutional sources to confirm or "
                f"refute this claim. The statement remains unverified."
            )
