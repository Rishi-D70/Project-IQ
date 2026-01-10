import re
from datetime import datetime
from core.schema import SCHEMA

class SchemaNormalizer:
    def normalize(self, contract: dict) -> dict:
        normalized = {}

        for field, rules in SCHEMA.items():
            value = contract.get(field)
            if value is None:
                normalized[field] = None
                continue

            field_type = rules["type"]

            if field_type == "object":
                normalized[field] = self._normalize_object(field, value)

            elif field_type == "date":
                normalized[field] = self._normalize_date(value)

            elif field_type == "int":
                normalized[field] = self._normalize_int(value)

            elif field_type == "country":
                normalized[field] = self._normalize_country(value)

            else:  # string or unknown
                normalized[field] = value

        return normalized

    # ------------------------
    # Type Normalizers
    # ------------------------

    def _normalize_object(self, field, value):
        if field == "parties" and isinstance(value, dict):
            return {
                "service_provider": value.get("service_provider") or value.get("party1"),
                "client": value.get("client") or value.get("party2")
            }
        return value

    def _normalize_date(self, value):
        if not isinstance(value, str):
            return value

        for fmt in ("%Y-%m-%d", "%d %B %Y"):
            try:
                dt = datetime.strptime(value, fmt)
                return dt.strftime("%d %B %Y")
            except Exception:
                continue

        return value  # fallback

    def _normalize_int(self, value):
        if isinstance(value, int):
            return value

            # Case 2: object with directional values
        if isinstance(value, dict):
            nums = []
            for v in value.values():
                if isinstance(v, int):
                    nums.append(v)
                elif isinstance(v, str):
                    match = re.search(r"\d+", v)
                    if match:
                        nums.append(int(match.group()))
            if nums:
                return min(nums)  # conservative choice
            return None

            # Case 3: string
        if isinstance(value, str):
            match = re.search(r"\d+", value)
            if match:
                return int(match.group())

            word_map = {
                "thirty": 30,
                "sixty": 60,
                "ninety": 90
            }
            for word, num in word_map.items():
                if word in value.lower():
                    return num

        return None

    def _normalize_country(self, value):
        if not isinstance(value, str):
            return value

        value = value.lower()

        if "india" in value:
            return "India"
        if "united states" in value or "usa" in value:
            return "United States"
        if "england" in value or "uk" in value:
            return "United Kingdom"

        return value
