import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from backend.core.evidence_store import ResearchTask
from backend.config import settings

# Lazy placeholders for heavy ML dependencies
torch = None
AutoTokenizer = None
AutoModelForSeq2SeqLM = None

logger = logging.getLogger(__name__)

class LLMManagerAgent:
    """
    Component 1: LLM Manager & Orchestrator
    Powered by FLAN-T5 (google/flan-t5-small / flan-t5-base) or Gemini API.
    
    Responsibilities:
    1. Understand user's request and classify intent:
       - Case 1: Mathematical expression (e.g. '2 + 2', '25 * 4', 'sqrt(144)') -> Calculator
       - Case 2: Factual research claim (e.g. 'Sri Lanka is surrounded by water.') -> Multi-Agent Pipeline
       - Case 3: Normal informational/conceptual question (e.g. 'What is artificial intelligence?') -> Informational Answer
    2. Decompose claims into targeted research tasks for:
       - Research Agent 1 (Supporting Evidence / Wikipedia)
       - Research Agent 2 (Alternative / Counter-evidence & Live Web DDGS)
    3. Coordinate agent workflow and information routing.
    
    Note: The LLM is NEVER used as the final truth detector. Evidence-level verification
    is strictly conducted by the NLI model (RoBERTa-large-MNLI / DeBERTa-v3).
    """

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or getattr(settings, "LLM_MODEL_NAME", "google/flan-t5-small")
        self.tokenizer = None
        self.model = None
        self.has_llm = False
        self.has_api_llm = False
        self._init_attempted = False

    def _ensure_model_loaded(self):
        """Lazy initialization: only loads model when first text generation is requested."""
        if self._init_attempted:
            return
        self._init_attempted = True

        import os

        # Check if Gemini API key is provided for 0-RAM Cloud LLM execution
        gemini_key = getattr(settings, "GEMINI_API_KEY", "") or os.getenv("GEMINI_API_KEY", "")
        if gemini_key:
            self.has_api_llm = True
            logger.info("LLM Manager using Google Gemini 1.5 API (0 MB server RAM overhead).")
            return

        global torch, AutoTokenizer, AutoModelForSeq2SeqLM
        if torch is None:
            try:
                import torch
                from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
            except ImportError:
                logger.info("Transformers not installed; LLM Manager running in structured heuristic mode.")
                return

        # Safeguard: Render free tier (512 MB RAM limit) cannot fit flan-t5-base (990 MB weights)
        if "base" in self.model_name.lower():
            logger.warning(
                f"{self.model_name} requires ~1.1 GB RAM, which exceeds Render's 512 MB limit. "
                "Automatically selecting memory-efficient google/flan-t5-small (~300 MB) or structured agentic mode."
            )
            self.model_name = "google/flan-t5-small"

        # 1. First attempt: Load from local cache without network blocking
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, local_files_only=True)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name, local_files_only=True)
            self.model.eval()
            self.has_llm = True
            logger.info(f"LLM Manager loaded local cached {self.model_name}.")
            return
        except Exception:
            pass

        # 2. Check if auto-download is explicitly enabled via environment
        allow_download = os.getenv("ENABLE_LLM_DOWNLOAD", "false").lower() == "true"
        if allow_download:
            try:
                logger.info(f"Downloading compact {self.model_name} from Hugging Face Hub...")
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
                self.model.eval()
                self.has_llm = True
                logger.info(f"LLM Manager loaded {self.model_name} from Hub.")
                return
            except Exception as e:
                logger.warning(f"Could not download {self.model_name}: {e}")

        logger.info("LLM Manager operating in structured agentic planning mode (zero latency, zero memory overhead).")
        self.has_llm = False

    def is_available(self) -> bool:
        self._ensure_model_loaded()
        return self.has_llm or self.has_api_llm

    def generate_text(self, prompt: str, max_length: int = 150) -> Optional[str]:
        self._ensure_model_loaded()

        # Option A: Cloud LLM API (Gemini)
        if self.has_api_llm:
            try:
                import requests
                api_key = getattr(settings, "GEMINI_API_KEY", "")
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                payload = {"contents": [{"parts": [{"text": prompt}]}]}
                resp = requests.post(url, json=payload, timeout=8)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", "").strip()
            except Exception as e:
                logger.warning(f"Gemini API generation error: {e}")

        # Option B: Local HuggingFace Seq2Seq Model
        if not self.has_llm or not self.tokenizer or not self.model:
            return None
        try:
            inputs = self.tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=max_length,
                    num_beams=2,
                    early_stopping=True
                )
            result = self.tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
            return result
        except Exception as e:
            logger.warning(f"LLM text generation error: {e}")
            return None
        finally:
            import gc
            gc.collect()

    def classify_intent(self, query: str) -> str:
        """
        Determines the query routing:
        - 'MATHEMATICAL': Pure arithmetic, equations, percentage, comparisons
        - 'INFORMATIONAL': Conceptual inquiries ('What is...', 'Explain...')
        - 'FACTUAL_CLAIM': Factual propositions to verify
        """
        q = query.strip()
        q_lower = q.lower()

        # Check pure math / arithmetic patterns
        # e.g., '2 + 2', '25 * 4', '100 / 5', 'sqrt(144)', '2 + 2 = 5', '10 x 5 = 50'
        if re.match(r'^\s*(?:sqrt|sin|cos|tan|log|pow|abs)?\s*\(?[\d\s+\-*/^%xX×=<>.]+\)?\s*$', q):
            return "MATHEMATICAL"

        if any(term in q_lower for term in ["sqrt(", "pow(", "log("]):
            return "MATHEMATICAL"

        if re.search(r'^\s*\d+\s*(?:[+\-*/^%xX×]|is\s+less\s+than|is\s+greater\s+than)\s*\d+\s*$', q, re.IGNORECASE):
            return "MATHEMATICAL"

        # Check informational questions (Case 3)
        # e.g. "What is artificial intelligence?", "Explain machine learning", "Define quantum computing"
        info_prefixes = [
            "what is ", "what are ", "what does ", "how does ", "explain ",
            "define ", "tell me about ", "describe ", "who was ", "who is ",
            "why is ", "why do ", "meaning of "
        ]
        if any(q_lower.startswith(p) for p in info_prefixes) and not any(term in q_lower for term in [" = ", " == ", " > ", " < "]):
            # Verify if it's an informational question vs a claim phrased with 'is'
            # e.g., "Is the Sun hot?" is a claim phrased as question, but "What is the Sun?" is informational
            return "INFORMATIONAL"

        # Default: Case 2 Factual Claim
        return "FACTUAL_CLAIM"

    def plan_research_tasks(self, claim: str) -> List[ResearchTask]:
        """
        Decomposes the claim into targeted research tasks for dual agents:
        - Research Agent 1: Supporting evidence & authoritative definition
        - Research Agent 2: Alternative perspectives, counterexamples, or refutations
        """
        tasks = []

        # If LLM is available, we can prompt it to generate targeted queries
        llm_subqueries = None
        if self.has_llm:
            prompt = (
                f"Task: Generate two targeted search queries to verify this claim: \"{claim}\".\n"
                f"Query 1 (supporting evidence):\n"
                f"Query 2 (counter-evidence or refutation):"
            )
            out = self.generate_text(prompt, max_length=80)
            if out and len(out.split()) >= 3:
                llm_subqueries = out

        # Fallback / Structured Heuristic Generation
        # Task 1: Primary encyclopedic / entity query
        clean_q1 = re.sub(r'\b(is|are|was|were|not|never|true|false)\b', '', claim, flags=re.IGNORECASE).strip()
        clean_q1 = re.sub(r'\s+', ' ', clean_q1)
        tasks.append(ResearchTask(
            task_id="task_1_supporting",
            query=claim,
            target_agent="ResearchAgent_1_Supporting",
            purpose=f"Gather authoritative reference and institutional evidence supporting the claim: '{claim}'"
        ))

        # Task 2: Alternative perspective / counter-evidence query
        # e.g. if claim is "All birds can fly", query for "flightless birds counterexamples"
        counter_query = claim
        if "all " in claim.lower():
            counter_query = claim.lower().replace("all ", "flightless ")
        elif "never" in claim.lower() or "not" in claim.lower():
            counter_query = re.sub(r'\b(not|never|cannot)\b', '', claim, flags=re.IGNORECASE).strip()

        tasks.append(ResearchTask(
            task_id="task_2_alternative",
            query=counter_query,
            target_agent="ResearchAgent_2_Alternative",
            purpose=f"Search for independent, alternative, or potentially contradicting evidence regarding: '{counter_query}'"
        ))

        return tasks
