import logging
from typing import Dict, Any, List, Optional, Tuple
from backend.core.models import FactVerdict
from backend.core.evidence_store import EvidenceStore

logger = logging.getLogger(__name__)

class EvidenceAggregatorAgent:
    """
    Evidence Aggregator:
    Combines NLI evaluation results across all gathered evidence sentences into an
    aggregated consensus verdict and calibrated confidence score.
    
    Rules:
    - Multiple reliable evidence items supporting claim -> FactVerdict.TRUE
    - Multiple reliable evidence items contradicting claim -> FactVerdict.FALSE
    - Significant conflicting evidence -> FactVerdict.PARTIALLY_TRUE
    - Insufficient or ambiguous evidence -> FactVerdict.UNVERIFIED
    """

    def aggregate(
        self,
        store: EvidenceStore,
        has_negation: bool = False,
        pos_prop: Optional[str] = None
    ) -> Tuple[FactVerdict, int, Optional[str]]:
        """
        Returns (Verdict, Confidence, SuggestedCorrectStatement).
        """
        evals = store.nli_evaluations

        # If no evaluations exist or no evidence gathered
        if not evals:
            return FactVerdict.UNVERIFIED, 30, None

        entail_scores = [e.confidence for e in evals if e.relation == "ENTAILMENT" and e.confidence >= 65]
        contra_scores = [e.confidence for e in evals if e.relation == "CONTRADICTION" and e.confidence >= 65]

        max_entail = max(entail_scores) if entail_scores else 0
        max_contra = max(contra_scores) if contra_scores else 0

        logger.info(f"Aggregation stats - Entailments: {len(entail_scores)} (max {max_entail}%), Contradictions: {len(contra_scores)} (max {max_contra}%)")

        # 1. Clear Contradiction Consensus
        if len(contra_scores) >= 1 and max_contra >= 70 and max_contra > max_entail:
            # If statement has negative polarity and positive proposition was contradicted,
            # then the negative statement itself is TRUE!
            if has_negation and pos_prop:
                logger.info("Negative claim proposition contradicted -> Negative statement is TRUE")
                conf = min(max_contra, 95)
                return FactVerdict.TRUE, conf, None

            conf = min(max_contra, 98)
            # Pick best contradicting evidence as basis for correction
            best_contra_text = store.contradicting_evidence[0] if store.contradicting_evidence else "The claim contradicts verified evidence."
            return FactVerdict.FALSE, conf, best_contra_text

        # 2. Clear Entailment Consensus
        if len(entail_scores) >= 1 and max_entail >= 70 and max_entail >= max_contra:
            # If statement has negative polarity and positive proposition was entailed,
            # then the negative statement is FALSE!
            if has_negation and pos_prop:
                logger.info("Negative claim proposition entailed -> Negative statement is FALSE")
                conf = min(max_entail, 95)
                return FactVerdict.FALSE, conf, pos_prop.capitalize()

            conf = min(max_entail, 98)
            return FactVerdict.TRUE, conf, None

        # 3. Mixed / Conflicting Evidence
        if len(entail_scores) >= 1 and len(contra_scores) >= 1:
            conf = int((max_entail + max_contra) / 2)
            return FactVerdict.PARTIALLY_TRUE, conf, "Evidence shows conflicting or partially valid aspects."

        # 4. Fallback / Insufficient Evidence
        return FactVerdict.UNVERIFIED, 35, None
