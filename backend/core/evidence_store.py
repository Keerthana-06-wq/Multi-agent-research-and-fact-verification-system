from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from backend.core.models import FactVerdict, SourceItem, ClaimCategory

@dataclass
class ResearchTask:
    task_id: str
    query: str
    target_agent: str  # e.g., "ResearchAgent_1_Supporting" or "ResearchAgent_2_Alternative"
    purpose: str

@dataclass
class NLIEvaluationItem:
    evidence_text: str
    source_title: str
    source_url: str
    relation: str  # ENTAILMENT, CONTRADICTION, NEUTRAL, UNKNOWN
    confidence: int

@dataclass
class EvidenceStore:
    """
    Evidence Store:
    Centralized in-memory data repository for tracking the lifecycle of verification:
    - User input & normalized claim
    - Decomposed research tasks
    - Collected & verified sources
    - Candidate evidence sentences
    - Evidence-level NLI evaluations
    - Supporting & contradicting evidence segments
    - Aggregated consensus scores & report
    """
    raw_query: str
    clean_claim: str = ""
    category: Optional[ClaimCategory] = None
    tasks: List[ResearchTask] = field(default_factory=list)
    sources: List[SourceItem] = field(default_factory=list)
    evidence_texts: List[str] = field(default_factory=list)
    nli_evaluations: List[NLIEvaluationItem] = field(default_factory=list)
    supporting_evidence: List[str] = field(default_factory=list)
    contradicting_evidence: List[str] = field(default_factory=list)
    verdict: FactVerdict = FactVerdict.UNVERIFIED
    confidence: int = 50
    correct_statement: Optional[str] = None
    explanation: str = ""
    is_informational: bool = False

    def add_source(self, source: SourceItem):
        if not any(s.url == source.url for s in self.sources):
            self.sources.append(source)

    def add_evidence(self, text: str):
        clean = text.strip()
        if clean and clean not in self.evidence_texts:
            self.evidence_texts.append(clean)

    def add_nli_evaluation(self, item: NLIEvaluationItem):
        self.nli_evaluations.append(item)
        if item.relation == "ENTAILMENT" and item.confidence >= 65:
            if item.evidence_text not in self.supporting_evidence:
                self.supporting_evidence.append(item.evidence_text)
        elif item.relation == "CONTRADICTION" and item.confidence >= 65:
            if item.evidence_text not in self.contradicting_evidence:
                self.contradicting_evidence.append(item.evidence_text)
