from core.document_loader import DocumentLoader
from core.chunker import TextChunker
from core.vector_store import VectorStore

def ingest_document(path: str) -> VectorStore:
    loader = DocumentLoader()
    text = loader.load_text(path)

    chunker = TextChunker(chunk_size=600, overlap=100)
    chunks = chunker.chunk(text)

    vector_store = VectorStore()
    vector_store.build_index(chunks)

    print(f"Ingestion complete. Indexed {len(chunks)} chunks.")
    return vector_store
