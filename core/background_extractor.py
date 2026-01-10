import threading

def start_background_extraction(ws, files):
    """
    Starts background extraction for an existing workspace.
    """
    # Prevent double-start
    if ws.extraction_status != "ingesting":
        print("Background extraction skipped, status:", ws.extraction_status)
        return

    thread = threading.Thread(
        target=run_extraction_pipeline,
        args=(ws, files),
        daemon=True
    )
    thread.start()


def run_extraction_pipeline(ws, files):
    try:
        ws.extraction_status = "extracting"
        ws.extraction_progress = 10

        from core.document_loader import DocumentLoader
        from core.chunker import TextChunker
        from core.vector_store import VectorStore
        from core.contract_extractor import ContractExtractor
        from core.llm_client import OllamaClient

        loader = DocumentLoader()
        full_text = ""

        for file_path in files:
            full_text += "\n" + loader.load_text(file_path)

        ws.raw_text = full_text
        ws.extraction_progress = 25

        chunker = TextChunker(chunk_size=600, overlap=100)
        chunks = chunker.chunk(full_text)
        ws.chunks = chunks
        ws.extraction_progress = 45

        vector_store = VectorStore()
        vector_store.build_index(chunks)
        ws.vector_store = vector_store
        ws.extraction_progress = 65
        print("[DEEP EXTRACTION] started")

        # 🔴 ACTUAL DEEP EXTRACTION (THIS WAS MISSING)
        llm = OllamaClient()
        extractor = ContractExtractor(llm)

        canonical = extractor.extract_from_chunks(chunks)
        print("[DEEP EXTRACTION] finished")
        print("[DEEP EXTRACTION] result keys:", canonical.keys() if canonical else None)

        ws.canonical_contract = canonical
        ws.extraction_progress = 90

        ws.extraction_status = "completed"
        ws.extraction_progress = 100

    except Exception as e:
        ws.extraction_status = "failed"
        ws.extraction_progress = 0
        ws.extraction_error = str(e)
