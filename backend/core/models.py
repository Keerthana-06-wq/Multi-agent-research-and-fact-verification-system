from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field

class ClaimCategory(str, Enum):
    MATHEMATICAL = "Mathematical"
    SCIENTIFIC = "Scientific"
    HISTORICAL = "Historical"
    GEOGRAPHICAL = "Geographical"
    SOCIAL = "Social"
    POLITICAL = "Political"
    TECHNOLOGICAL = "Technological"
    ENVIRONMENTAL = "Environmental"
    MEDICAL = "Medical"
    GENERAL_KNOWLEDGE = "General Knowledge"
    REAL_LIFE = "Real-life"
    CURRENT_EVENT = "Current Event"
    COMPARISON = "Comparison"
    LOGICAL = "Logical"
    MIXED = "Mixed"

class FactVerdict(str, Enum):
    TRUE = "TRUE"
    FALSE = "FALSE"
    UNVERIFIED = "UNVERIFIED"

class SourceTier(str, Enum):
    GOVERNMENT = "Government"
    ACADEMIC = "Academic / Research"
    SCIENTIFIC = "Scientific Institution"
    REPUTABLE_NEWS = "Reputable News"
    ENCYCLOPEDIC = "Reference / Encyclopedia"
    GENERAL_WEB = "General Web"

class SourceItem(BaseModel):
    title: str
    url: str
    domain: str
    snippet: str
    tier: str = SourceTier.GENERAL_WEB.value
    credibility_score: int = Field(default=50, ge=0, le=100)

class PartiallyTrueDetails(BaseModel):
    correct_part: str
    incorrect_part: str
    accurate_statement: str

class QualityChecks(BaseModel):
    extracted_correct_claim: bool = True
    ignored_suggested_answer: bool = True
    understood_complete_sentence: bool = True
    handled_negation: bool = True
    handled_universal_quantifiers: bool = True
    verified_numbers_dates: bool = True
    verified_comparisons: bool = True
    separated_multiple_claims: bool = True
    reasoning_before_search: bool = True
    reliable_evidence_used: bool = True
    unverified_rule_respected: bool = True

class SubClaimResult(BaseModel):
    claim: str
    verdict: FactVerdict
    explanation: str

class AgentTraceStep(BaseModel):
    agent_name: str
    status: str
    summary: str
    details: Optional[str] = None

class VerificationRequest(BaseModel):
    query: str

class VerificationResponse(BaseModel):
    claim: str
    category: ClaimCategory
    verdict: FactVerdict
    confidence: int = Field(ge=0, le=100)
    explanation: str
    evidence: List[str] = Field(default_factory=list)
    sources: List[SourceItem] = Field(default_factory=list)
    correct_statement: Optional[str] = None
    sub_claims: Optional[List[SubClaimResult]] = None
    quality_checks: QualityChecks = Field(default_factory=QualityChecks)
    agent_traces: List[AgentTraceStep] = Field(default_factory=list)
