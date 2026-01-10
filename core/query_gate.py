import re

# very strict, intentionally conservative
ALLOWED_KEYWORDS = [
    "contract", "agreement", "clause", "termination", "payment",
    "notice", "party", "obligation", "liability", "governing law",
    "jurisdiction", "effective date", "scope", "services"
]

def is_contract_query(question: str) -> bool:
    q = question.lower()

    # obvious disallowed intents
    blocked_patterns = [
        r"how to save",
        r"medical",
        r"suicide",
        r"die",
        r"kill",
        r"emergency",
        r"crime",
        r"hacking",
        r"personal advice"
    ]

    for p in blocked_patterns:
        if re.search(p, q):
            return False

    return any(k in q for k in ALLOWED_KEYWORDS)
