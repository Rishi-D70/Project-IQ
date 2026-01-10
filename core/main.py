from core.document_loader import DocumentLoader
from core.chunker import TextChunker
from core.llm_client import OllamaClient
from core.contract_extractor import ContractExtractor
import json

loader = DocumentLoader()
text = loader.load_text("MASTER SERVICES AGREEMENT.pdf")

chunker = TextChunker()
chunks = chunker.chunk(text)

llm = OllamaClient()
extractor = ContractExtractor(llm)

final_contract = extractor.extract_from_chunks(chunks)
print(json.dumps(final_contract, indent=2))
print(f"Total chunks: {len(chunks)}")

relevant = [c for c in chunks if extractor.filter.is_relevant(c)]
print(f"Relevant chunks sent to LLM: {len(relevant)}")
