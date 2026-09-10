import re
from typing import Dict, Any, List

class NegationDetectorAgent:
    """
    Step 9: Negative Statements Special Handler.
    1. Identifies negative words and phrases (NOT, DOES NOT, NEVER, CANNOT, WITHOUT, NO, etc.)
    2. Derives the underlying positive proposition.
    3. Enables evaluation of the positive proposition to determine the truth value of the negative statement.
    """

    NEGATION_PATTERNS = [
        r'\bwill\s+not\b', r'\bwon\'?t\b',
        r'\bdoes\s+not\b', r'\bdoesn\'?t\b',
        r'\bdo\s+not\b', r'\bdon\'?t\b',
        r'\bdid\s+not\b', r'\bdidn\'?t\b',
        r'\bcannot\b', r'\bcan\'?t\b',
        r'\bcould\s+not\b', r'\bcouldn\'?t\b',
        r'\bwould\s+not\b', r'\bwouldn\'?t\b',
        r'\bis\s+not\b', r'\bisn\'?t\b',
        r'\bare\s+not\b', r'\baren\'?t\b',
        r'\bwas\s+not\b', r'\bwasn\'?t\b',
        r'\bwere\s+not\b', r'\bweren\'?t\b',
        r'\bhas\s+not\b', r'\bhasn\'?t\b',
        r'\bhave\s+not\b', r'\bhaven\'?t\b',
        r'\bnever\b',
        r'\bno\s+longer\b',
        r'\bfails\s+to\b',
        r'\bimpossible\b',
        r'\bneither\b',
        r'\bnor\b',
        r'\bnot\b',
        r'\bno\b'
    ]

    INVERSION_RULES = [
        (r'\bwill\s+not\s+(\w+)\b', r'\1s'),
        (r'\bwon\'?t\s+(\w+)\b', r'\1s'),
        (r'\bdoes\s+not\s+(\w+)\b', r'\1s'),
        (r'\bdoesn\'?t\s+(\w+)\b', r'\1s'),
        (r'\bdo\s+not\s+(\w+)\b', r'\1'),
        (r'\bdon\'?t\s+(\w+)\b', r'\1'),
        (r'\bdid\s+not\s+(\w+)\b', r'\1ed'),
        (r'\bdidn\'?t\s+(\w+)\b', r'\1ed'),
        (r'\bis\s+not\b', 'is'),
        (r'\bisn\'?t\b', 'is'),
        (r'\bare\s+not\b', 'are'),
        (r'\baren\'?t\b', 'are'),
        (r'\bwas\s+not\b', 'was'),
        (r'\bwasn\'?t\b', 'was'),
        (r'\bcannot\s+(\w+)\b', r'can \1'),
        (r'\bcan\'?t\s+(\w+)\b', r'can \1'),
        (r'\bnever\s+(\w+)\b', r'\1'),
    ]

    def analyze(self, claim: str) -> Dict[str, Any]:
        text = claim.strip()
        lower = text.lower()

        found_negations: List[str] = []
        for pat in self.NEGATION_PATTERNS:
            matches = re.findall(pat, lower)
            if matches:
                found_negations.extend(matches)

        has_negation = len(found_negations) > 0
        polarity = "NEGATIVE" if has_negation else "POSITIVE"

        positive_proposition = text
        if has_negation:
            for pattern, replacement in self.INVERSION_RULES:
                if re.search(pattern, positive_proposition, flags=re.IGNORECASE):
                    positive_proposition = re.sub(pattern, replacement, positive_proposition, flags=re.IGNORECASE)
                    break
            # Clean up double 'ss'
            positive_proposition = re.sub(r'(\w+)ss\b', r'\1s', positive_proposition)
            positive_proposition = re.sub(r'\bnot\b', '', positive_proposition, flags=re.IGNORECASE)
            positive_proposition = re.sub(r'\s+', ' ', positive_proposition).strip()

        return {
            "has_negation": has_negation,
            "polarity": polarity,
            "negation_tokens": list(set(found_negations)),
            "positive_proposition": positive_proposition,
            "original_claim": text
        }
