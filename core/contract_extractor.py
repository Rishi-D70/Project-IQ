from core.merge_logic import ContractMerger
from core.rule_filter import RuleBasedFilter
from core.schema_normalizer import SchemaNormalizer



class ContractExtractor:
    def __init__(self, llm_client):
        self.llm = llm_client
        self.filter = RuleBasedFilter()
        self.normalizer = SchemaNormalizer()

    def extract_from_chunks(self, chunks: list[str]) -> dict:
        merger = ContractMerger()

        for chunk in chunks:

            if not self.filter.is_relevant(chunk):
                continue

            try:
                extracted, _ = self.llm.extract_contract_data(chunk)
                merger.merge(extracted)
            except Exception:
                continue

        merged = merger.get_result()
        normalizer = SchemaNormalizer()
        return normalizer.normalize(merged)


