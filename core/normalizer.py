import re
from datetime import datetime

class ContractNormalizer:
    def normalize(self, contract: dict) -> dict:
        contract = self._normalize_parties(contract)
        contract = self._normalize_effective_date(contract)
        contract = self._normalize_termination_notice(contract)
        contract = self._normalize_governing_law(contract)
        return contract

    # ----------------------------
    # Parties
    # ----------------------------
    def _normalize_parties(self, contract: dict) -> dict:
        parties = contract.get("parties")
        if not isinstance(parties, dict):
            return contract

        # Canonical keys
        service_provider = parties.get("service_provider") or parties.get("party1")
        client = parties.get("client") or parties.get("party2")

        contract["parties"] = {
            "service_provider": service_provider,
            "client": client
        }

        return contract

    # ----------------------------
    # Effective Date
    # ----------------------------
    def _normalize_effective_date(self, contract: dict) -> dict:
        date_val = contract.get("effective_date")
        if not isinstance(date_val, str):
            return contract

        # Try ISO format first
        try:
            dt = datetime.fromisoformat(date_val)
            contract["effective_date"] = dt.strftime("%d %B %Y")
            return contract
        except Exception:
            pass

        # Try common textual format
        try:
            dt = datetime.strptime(date_val, "%d %B %Y")
            contract["effective_date"] = dt.strftime("%d %B %Y")
        except Exception:
            pass

        return contract

    # ----------------------------
    # Termination Notice Days
    # ----------------------------
    def _normalize_termination_notice(self, contract: dict) -> dict:
        val = contract.get("termination_notice_days")

        if isinstance(val, int):
            return contract

        if isinstance(val, str):
            # Extract digits if present
            match = re.search(r"\d+", val)
            if match:
                contract["termination_notice_days"] = int(match.group())
                return contract

            # Fallback: word-to-number map
            word_map = {
                "thirty": 30,
                "sixty": 60,
                "ninety": 90
            }

            for word, num in word_map.items():
                if word in val.lower():
                    contract["termination_notice_days"] = num
                    return contract

        return contract

    # ----------------------------
    # Governing Law
    # ----------------------------
    def _normalize_governing_law(self, contract: dict) -> dict:
        law = contract.get("governing_law")

        if not isinstance(law, str):
            return contract

        law = law.lower()

        if "india" in law:
            contract["governing_law"] = "India"
        elif "united states" in law or "usa" in law:
            contract["governing_law"] = "United States"
        elif "england" in law or "uk" in law:
            contract["governing_law"] = "United Kingdom"

        return contract
