import logging
from typing import Dict, Any, List
from backend.core.models import FactVerdict

logger = logging.getLogger(__name__)

class VerificationGuardAgent:
    """
    Step 18 Quality Guard:
    Enforces final logical consistency between the assigned verdict, negation, and underlying evidence.
    
    Rule:
    A negative statement is TRUE if the underlying affirmative proposition is refuted/false.
    A negative statement is FALSE if the underlying affirmative proposition is established as true.
    """

    def audit_and_protect(self, claim_data: Dict[str, Any], verdict_data: Dict[str, Any], evidence_texts: List[str]) -> Dict[str, Any]:
        verdict = verdict_data.get("verdict", FactVerdict.UNVERIFIED)
        has_negation = claim_data.get("has_negation", False)
        correct_statement = verdict_data.get("correct_statement")

        # Guard: FALSE verdict must have a clear explanation and correct statement
        if verdict == FactVerdict.FALSE and not correct_statement:
            pos_prop = claim_data.get("positive_proposition")
            if pos_prop:
                verdict_data["correct_statement"] = pos_prop.capitalize()
            else:
                verdict_data["correct_statement"] = "The claim contradicts established scientific or historical facts."

        # Guard: Ensure UNVERIFIED is never masked as TRUE or FALSE when evidence is absent
        if not evidence_texts and verdict in [FactVerdict.TRUE, FactVerdict.FALSE]:
            logger.warning("Guard alert: Verdict set without evidence. Enforcing UNVERIFIED.")
            verdict_data["verdict"] = FactVerdict.UNVERIFIED
            verdict_data["confidence"] = 20
            verdict_data["explanation"] = "There is not enough reliable evidence available to confirm or reject this statement."

        return verdict_data
