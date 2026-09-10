import re

class ClaimNormalizerAgent:
    """
    Agent 4: Claim Normalization Agent
    Normalizes user claims into clear, grammatical propositions for semantic evaluation.
    Removes bias artifacts and cleans syntax.
    """

    GRAMMAR_FIXES = [
        (r'\bwill\s+not\s+turns\b', 'will not turn'),
        (r'\bdoes\s+not\s+turns\b', 'does not turn'),
        (r'\bdo\s+not\s+turns\b', 'do not turn'),
        (r'\bdid\s+not\s+turns\b', 'did not turn'),
        (r'\bcannot\s+turns\b', 'cannot turn'),
        (r'\bwill\s+not\s+revolves\b', 'will not revolve'),
        (r'\bdoes\s+not\s+revolves\b', 'does not revolve'),
    ]

    def normalize(self, raw_claim: str) -> str:
        text = raw_claim.strip()
        # Remove trailing true / false supplied by user as confirmation bias
        text = re.sub(r'\s+(true|false|correct|incorrect)\s*$', '', text, flags=re.IGNORECASE)
        # Remove leading verification phrases
        patterns = [
            r'^(please\s+)?verify(\s+this)?\s*:\s*',
            r'^(please\s+)?verify\s+if\s+',
            r'^(please\s+)?verify\s+that\s+',
            r'^(is\s+it\s+true\s+(that)?\s*)',
            r'^(is\s+this\s+true\s*:\s*)',
            r'^(can\s+you\s+verify\s+(if|that)?\s*)',
            r'^(i\s+think\s+(that)?\s*)',
            r'^(is\s+it\s+correct\s+(that)?\s*)'
        ]
        for p in patterns:
            text = re.sub(p, '', text, flags=re.IGNORECASE)

        # Apply grammar fixes
        for pattern, replacement in self.GRAMMAR_FIXES:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

        # Capitalize first letter, ensure single spaces
        text = re.sub(r'\s+', ' ', text).strip()
        if text and text[0].islower():
            text = text[0].upper() + text[1:]

        return text
