class ContractMerger:
    def __init__(self):
        self.result = {}

    def merge(self, partial: dict):
        """
        Merge one partial extraction into the final contract state.
        """
        for key, value in partial.items():
            if value is None:
                continue

            if key not in self.result or self.result[key] is None:
                # Field not set yet
                self.result[key] = value
            else:
                # Field already exists → resolve carefully
                self._resolve_conflict(key, value)

    def _resolve_conflict(self, key: str, new_value):
        """
        Field-specific conflict resolution rules.
        """
        existing = self.result[key]

        # 1️⃣ Parties (nested object)
        if key == "parties" and isinstance(existing, dict):
            for sub_key, sub_val in new_value.items():
                if sub_val is None:
                    continue
                if sub_key not in existing or existing[sub_key] is None:
                    existing[sub_key] = sub_val
            self.result[key] = existing
            return

        # 2️⃣ Termination notice days (numeric)
        if key == "termination_notice_days":
            try:
                existing_days = int(existing)
                new_days = int(new_value)
                # Conservative rule: keep smaller notice period
                self.result[key] = min(existing_days, new_days)
            except Exception:
                pass
            return

        # 3️⃣ All other fields
        # First non-null wins → do nothing
        return

    def get_result(self) -> dict:
        return self.result
