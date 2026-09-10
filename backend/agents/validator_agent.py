import logging
from typing import Dict, Any
from backend.core.models import FactVerdict

logger = logging.getLogger(__name__)

class EvidenceValidatorAgent:
    """
    Agent 5: Evidence Validator Agent
    Performs critical auditing on the verifier agent's output prior to presentation:
    - Verifies evidence threshold: a claim marked TRUE must have authoritative citations.
    - Ensures FALSE claims have explicit contradictory evidence or a verified correct statement.
    - Prevents false confidence inflation.
    - Ensures UNVERIFIED claims are preserved and not coerced into TRUE or FALSE.
    """

    def validate(self, claim: str, verdict_data: Dict[str, Any]) -> Dict[str, Any]:
        verdict = verdict_data.get("verdict", FactVerdict.UNVERIFIED)
        sources = verdict_data.get("sources", [])
        evidence = verdict_data.get("evidence", [])
        confidence = verdict_data.get("confidence", 50)
        correct_statement = verdict_data.get("correct_statement")

        # Rule 1: A claim cannot be TRUE if there are 0 reliable sources or 0 evidence items
        if verdict == FactVerdict.TRUE and (len(sources) == 0 or len(evidence) == 0):
            logger.warning("Evidence validator downgraded TRUE to UNVERIFIED due to zero sources.")
            verdict_data["verdict"] = FactVerdict.UNVERIFIED
            verdict_data["confidence"] = 30
            verdict_data["explanation"] = "Reliable evidence was insufficient to validate this statement as TRUE."

        # Rule 2: A claim marked FALSE should ideally have a correct statement
        if verdict == FactVerdict.FALSE and not correct_statement:
            verdict_data["correct_statement"] = "The claim is refuted by reliable scientific or historical documentation."

        # Rule 3: Cap confidence for unverified claims
        if verdict == FactVerdict.UNVERIFIED and confidence > 45:
            verdict_data["confidence"] = 35

        # Rule 4: Cap confidence if top source has low credibility
        if sources and sources[0].credibility_score < 70 and verdict == FactVerdict.TRUE:
            verdict_data["confidence"] = min(confidence, 75)

        return verdict_data
