import re

class RuleBasedFilter:
    def __init__(self):
        # Keywords mapped to fields they indicate
        self.rules = {
            "parties": [
                "by and between", "party", "parties", "service provider", "client"
            ],
            "effective_date": [
                "effective date", "entered into on", "dated", "as of"
            ],
            "termination_notice_days": [
                "terminate", "termination", "notice", "written notice"
            ],
            "payment_amount": [
                "payment", "fee", "consideration", "invoice", "payable", "amount"
            ],
            "governing_law": [
                "governing law", "jurisdiction", "laws of", "courts of"
            ]
        }

    def is_relevant(self, chunk: str) -> bool:
        """
        Returns True if the chunk contains any signal worth sending to the LLM.
        """
        text = chunk.lower()

        for keywords in self.rules.values():
            for kw in keywords:
                if kw in text:
                    return True

        return False
