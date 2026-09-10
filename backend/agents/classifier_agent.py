import re
from typing import Tuple, List, Optional
from backend.core.models import ClaimCategory

class InputClassifierAgent:
    """
    Step 1 & Step 3: Identify the Claim and Classify Category.
    Strips user instructions ('true', 'false', 'verify this', 'is this true?').
    Categorizes the claim into:
    MATHEMATICAL, SCIENTIFIC, HISTORICAL, GEOGRAPHICAL, SOCIAL, POLITICAL,
    TECHNOLOGICAL, ENVIRONMENTAL, MEDICAL, GENERAL_KNOWLEDGE, REAL_LIFE,
    CURRENT_EVENT, COMPARISON, LOGICAL, MIXED.
    """

    MATH_OPERATORS = set("+-*/^%()=<>")

    COMPARISON_TERMS = [
        "greater than", "less than", "larger than", "smaller than",
        "older than", "younger than", "faster than", "slower than",
        "more than", "fewer than", "taller than", "shorter than",
        "heavier than", "lighter than", "higher than", "lower than"
    ]

    GEOGRAPHY_KEYWORDS = [
        "capital", "country", "continent", "ocean", "river", "mountain",
        "border", "located in", "in asia", "in europe", "in africa",
        "in north america", "in south america", "in australia", "in antarctica",
        "desert", "city", "island", "sea", "lake", "north of", "south of"
    ]

    SCIENCE_KEYWORDS = [
        "revolve", "orbit", "planet", "sun", "earth", "moon", "star",
        "freeze", "boil", "liquid", "gas", "solid", "oxygen", "hydrogen",
        "nitrogen", "water", "gravity", "cell", "dna", "atom", "molecule",
        "energy", "photosynthesis", "speed of light", "temperature", "mass"
    ]

    REAL_LIFE_KEYWORDS = [
        "human", "humans", "breathe", "survive", "drink", "food", "sleep",
        "bird", "birds", "fish", "fly", "walk", "live in", "live on",
        "underwater", "equipment"
    ]

    HISTORICAL_KEYWORDS = [
        "independent", "independence", "war", "battle", "treaty", "empire",
        "century", "invented", "discovered", "founded", "revolution", "dynasty",
        "ancient", "1947", "1876", "1776", "1914", "1939", "1945"
    ]

    POLITICAL_KEYWORDS = [
        "president", "prime minister", "parliament", "congress", "senate",
        "constitution", "minister", "governor", "democracy", "election",
        "republic", "monarchy"
    ]

    TECHNOLOGICAL_KEYWORDS = [
        "computer", "software", "artificial intelligence", "internet", "cpu",
        "gpu", "algorithm", "python", "programming", "robot", "microchip"
    ]

    def extract_claim(self, raw_input: str) -> Tuple[str, bool]:
        """
        Step 1: Extract the clean proposition.
        Ignore words such as: 'true', 'false', 'correct', 'incorrect', 'is this true?',
        'verify this', 'I think this is true'.
        Returns (clean_claim, had_suggested_answer).
        """
        text = raw_input.strip()
        had_suggested = False

        # Remove trailing suggestion words (e.g. 'India became independent in 1947 true')
        trailing_match = re.search(r'\s+(true|false|correct|incorrect)\s*$', text, flags=re.IGNORECASE)
        if trailing_match:
            had_suggested = True
            text = text[:trailing_match.start()].strip()

        # Remove leading verification phrases
        patterns = [
            r'^(please\s+)?verify(\s+this)?\s*:\s*',
            r'^(please\s+)?verify\s+(if|that)?\s*',
            r'^(is\s+it\s+true\s+(that)?\s*)',
            r'^(is\s+this\s+true\s*:\s*)',
            r'^(can\s+you\s+verify\s+(if|that)?\s*)',
            r'^(i\s+think\s+(that)?\s*)',
            r'^(is\s+it\s+correct\s+(that)?\s*)',
            r'^(tell\s+me\s+if\s+)',
            r'^(check\s+if\s+)'
        ]
        for p in patterns:
            if re.search(p, text, flags=re.IGNORECASE):
                had_suggested = True
                text = re.sub(p, '', text, flags=re.IGNORECASE).strip()

        # Remove question marks at the end if it's a claim phrased as question
        # e.g. "Is the Earth round?" -> "The Earth is round" (handled if needed)
        text = re.sub(r'^\s*is\s+(the\s+.+?)\s*\?\s*$', r'\1 is', text, flags=re.IGNORECASE)
        text = text.rstrip("?").strip()

        return text, had_suggested

    def is_mathematical(self, text: str) -> bool:
        # Check if text contains arithmetic or algebraic equations
        # e.g., '2 + 2 = 4', '2 + 2 = 5', '10 x 5 = 50', '100 is less than 20', '25% of 200 is 50', '(25 + 15) * 2'
        if re.search(r'\b\d+\s*[%xX*+/^-]\s*\d+', text):
            return True
        if re.search(r'\b\d+\s*(?:==|=|<|>|<=|>=)\s*\d+', text):
            return True
        if re.search(r'\b\d+\s+(?:is\s+(?:greater|less|more|equal)\s+(?:than|to))\s+\d+', text, flags=re.IGNORECASE):
            return True
        if re.search(r'\b\d+%\s+of\s+\d+\s+is\s+\d+\b', text, flags=re.IGNORECASE):
            return True
        if any(op in text for op in ['+', '*', '/', '^']) and any(c.isdigit() for c in text):
            return True
        return False

    def is_comparison(self, text: str) -> bool:
        lower = text.lower()
        return any(term in lower for term in self.COMPARISON_TERMS)

    def separate_multiple_claims(self, text: str) -> Optional[List[str]]:
        """
        Step 12: If one sentence contains multiple factual claims joined by 'and', separate them.
        Example: 'India became independent in 1947 and Mumbai is the capital of India.'
        """
        # Look for ' and ' where both sides look like complete clauses with subject-verb
        parts = re.split(r'\s+and\s+', text, flags=re.IGNORECASE)
        if len(parts) >= 2:
            # Check if each part contains a verb
            verb_pattern = r'\b(is|are|was|were|became|has|have|had|revolves|contains|turns|lives|can)\b'
            if all(re.search(verb_pattern, p, flags=re.IGNORECASE) for p in parts):
                return [p.strip() for p in parts]
        return None

    def classify(self, text: str) -> ClaimCategory:
        lower = text.lower()

        # 1. Multiple claims -> MIXED
        multi = self.separate_multiple_claims(text)
        if multi and len(multi) > 1:
            return ClaimCategory.MIXED

        # 2. Mathematical Check
        if self.is_mathematical(text):
            return ClaimCategory.MATHEMATICAL

        # 3. Comparison Check
        if self.is_comparison(text):
            return ClaimCategory.COMPARISON

        # 4. Political Check
        if any(k in lower for k in self.POLITICAL_KEYWORDS):
            return ClaimCategory.POLITICAL

        # 5. Geography Check
        if any(k in lower for k in self.GEOGRAPHY_KEYWORDS):
            return ClaimCategory.GEOGRAPHICAL

        # 6. Technology Check
        if any(k in lower for k in self.TECHNOLOGICAL_KEYWORDS):
            return ClaimCategory.TECHNOLOGICAL

        # 7. History Check
        if any(k in lower for k in self.HISTORICAL_KEYWORDS):
            return ClaimCategory.HISTORICAL

        # 8. Science Check
        if any(k in lower for k in self.SCIENCE_KEYWORDS):
            return ClaimCategory.SCIENTIFIC

        # 9. Real-life Check
        if any(k in lower for k in self.REAL_LIFE_KEYWORDS):
            return ClaimCategory.REAL_LIFE

        return ClaimCategory.GENERAL_KNOWLEDGE
