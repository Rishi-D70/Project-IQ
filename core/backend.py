from core.background_extractor import start_background_extraction
from core.workspace_manager import WorkspaceManager
from core.document_loader import DocumentLoader
from core.chunker import TextChunker
from core.vector_store import VectorStore
from core.contract_extractor import ContractExtractor
from core.llm_client import OllamaClient
from core.query_gate import is_contract_query
import threading
from core.query_router import resolve_requested_fields

workspace_manager = WorkspaceManager()


# -------------------------
# INGEST
# -------------------------

def ingest(files: list[str]) -> dict:
    """
    Fast ingestion endpoint.
    - Registers workspace immediately
    - Starts background processing
    - Returns workspace ID instantly
    """

    if not files:
        return {
            "workspace_id": None,
            "status": "failed",
            "error": "No files provided"
        }

    ws = workspace_manager.create_workspace()
    ws.files = files

    # Explicit initial status
    ws.extraction_status = "ingesting"
    ws.extraction_progress = 0

    # Start background processing
    # Note: start_background_extraction should update ws status
    start_background_extraction(ws, files)

    return {
        "workspace_id": ws.id,
        "status": ws.extraction_status
    }


# -------------------------
# Helper function for RAG context (if missing)
# -------------------------

def build_rag_context(vector_store, question, top_k=5):
    """
    Build context from vector store for RAG
    """
    if not vector_store:
        return ""

    try:
        # If vector_store has a query method
        if hasattr(vector_store, 'query'):
            results = vector_store.query(question, top_k=top_k)
            if isinstance(results, dict) and 'sources' in results:
                return "\n".join(results['sources'])
            elif isinstance(results, list):
                return "\n".join(results)

        # If vector_store has chunks
        if hasattr(vector_store, 'chunks') and vector_store.chunks:
            # Simple similarity search (you should implement proper vector search)
            chunks = vector_store.chunks[:top_k]
            return "\n".join(chunks)

        return ""
    except Exception as e:
        print(f"Error building RAG context: {e}")
        return ""


# -------------------------
# QUERY
# -------------------------

def query(workspace_id: str, question: str, mode: str = "answer") -> dict:
    """
    Complete query function with debugging and proper RAG integration
    """
    print(f"\n{'=' * 80}")
    print(f"QUERY FUNCTION CALLED")
    print(f"{'=' * 80}")
    print(f"Workspace ID: {workspace_id}")
    print(f"Question: {question}")
    print(f"Mode: {mode}")

    # -----------------------------
    # Workspace validation
    # -----------------------------
    ws = workspace_manager.get_workspace(workspace_id)
    if not ws:
        print(f"ERROR: Workspace {workspace_id} not found")
        return {
            "type": "error",
            "message": "Invalid workspace ID."
        }

    print(f"✓ Workspace found: {ws.id}")
    print(f"  Extraction status: {getattr(ws, 'extraction_status', 'unknown')}")
    print(f"  Files: {getattr(ws, 'files', [])}")

    # -----------------------------
    # Mode validation
    # -----------------------------
    if mode not in {"answer", "table", "export"}:
        print(f"ERROR: Invalid mode: {mode}")
        return {
            "type": "error",
            "message": "Invalid query mode. Use 'answer', 'table', or 'export'."
        }

    # -----------------------------
    # ANSWER MODE (RAG)
    # -----------------------------
    if mode == "answer":
        print(f"\n--- STARTING RAG QUERY ---")

        # Check if vector store exists
        if not hasattr(ws, 'vector_store'):
            print(f"ERROR: Workspace has no vector_store attribute")
            return {
                "type": "error",
                "message": "Document processing not complete. Please wait."
            }

        if not ws.vector_store:
            print(f"ERROR: vector_store is None")
            return {
                "type": "error",
                "message": "Document processing failed. Vector store not created."
            }

        print(f"✓ Vector store available")
        print(f"  Type: {type(ws.vector_store)}")

        # Debug: Check vector store methods
        vector_methods = [m for m in dir(ws.vector_store) if not m.startswith('_')]
        print(f"  Available methods: {vector_methods}")

        # Debug: Check if vector store has chunks
        if hasattr(ws.vector_store, 'chunks'):
            chunk_count = len(ws.vector_store.chunks)
            print(f"  Has chunks: Yes ({chunk_count} chunks)")
            if chunk_count > 0:
                print(f"  First chunk preview: {ws.vector_store.chunks[0][:200]}...")
        else:
            print(f"  Has chunks: No")

        # Build context using RAG
        print(f"\nBuilding RAG context...")
        context = build_rag_context(ws.vector_store, question)
        print(f"Context length: {len(context)} characters")

        if not context or len(context.strip()) < 10:
            print(f"WARNING: Context is empty or too short!")
            print(f"Context content: '{context}'")

            # Try alternative method to get context
            print(f"\nTrying alternative context extraction...")
            alternative_context = get_context_fallback(ws.vector_store, question)
            if alternative_context and len(alternative_context) > 10:
                context = alternative_context
                print(f"✓ Got context from fallback: {len(context)} chars")
            else:
                print(f"✗ Fallback also failed")

        # Create prompt
        prompt = f"""
SYSTEM RULES (MANDATORY):
- You are a contract analysis assistant.
- Answer ONLY using the contract context below.
- If the answer is not explicitly present, say: "The contract doesn't specify this clearly."
- Be concise and factual.
- Do not make up information.

CONTRACT CONTEXT:
{context}

QUESTION:
{question}

ANSWER (based only on contract context):
"""

        print(f"\nSending to LLM...")
        print(f"Prompt length: {len(prompt)} characters")
        print(f"Prompt preview:\n{prompt[:500]}...")

        try:
            # Try to use RAGQueryEngine if available
            try:
                from core.rag_query import RAGQueryEngine
                print(f"✓ Using RAGQueryEngine")
                rag_engine = RAGQueryEngine(ws.vector_store)
                answer = rag_engine.answer(question)
                print(f"✓ RAGQueryEngine answer received: {len(answer)} chars")
            except ImportError:
                print(f"✗ RAGQueryEngine not available, using direct LLM")
                llm = OllamaClient()
                answer = llm.ask(prompt).strip()
                print(f"✓ Direct LLM answer received: {len(answer)} chars")
            except Exception as rag_error:
                print(f"✗ RAGQueryEngine failed: {rag_error}")
                print(f"  Falling back to direct LLM...")
                llm = OllamaClient()
                answer = llm.ask(prompt).strip()
                print(f"✓ Fallback LLM answer: {len(answer)} chars")

            if not answer or answer.strip() == "":
                print(f"WARNING: Empty answer from LLM")
                answer = "The contract doesn't provide clear information on this."

            print(f"\nAnswer preview: {answer[:200]}...")

            return {
                "type": "text",
                "data": answer
            }

        except Exception as e:
            print(f"\nERROR in LLM call: {str(e)}")
            import traceback
            traceback.print_exc()

            return {
                "type": "error",
                "message": f"Failed to get answer: {str(e)}"
            }

    # -----------------------------
    # TABLE / EXPORT REQUIRE EXTRACTION
    # -----------------------------
    if not hasattr(ws, 'extraction_status'):
        print(f"ERROR: Workspace has no extraction_status")
        return {
            "type": "error",
            "message": "Workspace not properly initialized."
        }

    if ws.extraction_status != "completed":
        print(f"ERROR: Extraction not complete. Status: {ws.extraction_status}")
        return {
            "type": "error",
            "message": f"Contract analysis is still processing (status: {ws.extraction_status}). Please wait."
        }

    # -----------------------------
    # TABLE MODE (Placeholder)
    # -----------------------------
    import json
    if mode == "table":
        from core.table_builder import build_table

        fields = resolve_requested_fields(question)

        if not fields:
            return {
                "type": "error",
                "message": "No recognizable contract fields requested."
            }

        table = build_table(
            ws.canonical_contract,
            allowed_fields=fields
        )

        print(f"DEBUG - Table data before return:")
        print(f"  Type: {type(table)}")
        print(f"  Content: {table}")
        print(f"  Is dict: {isinstance(table, dict)}")

        # Ensure it's a dict, not a string
        if isinstance(table, str):
            try:
                table = json.loads(table)
                print(f"  Parsed from string: {table}")
            except:
                pass

        return table


    # -----------------------------
    # EXPORT MODE (Placeholder)
    # -----------------------------
    if mode == "export":
        print(f"\nEXPORT MODE requested (not implemented)")
        return {
            "type": "redirect",
            "url": "#",
            "message": "Export feature is under development."
        }

    print(f"\n{'=' * 80}")
    print(f"QUERY COMPLETED")
    print(f"{'=' * 80}")

    # Should not reach here, but just in case
    return {
        "type": "error",
        "message": "Unexpected error in query processing."
    }


def build_rag_context(vector_store, question, top_k=5):
    """
    Build context from vector store for RAG - with fallback methods
    """
    print(f"\n  Building RAG context for question: '{question}'")

    if not vector_store:
        print(f"  ERROR: vector_store is None")
        return ""

    try:
        # Method 1: Try search() method
        if hasattr(vector_store, 'search') and callable(vector_store.search):
            print(f"  Using vector_store.search()")
            try:
                chunks = vector_store.search(question, k=top_k)
                print(f"  Search returned: {len(chunks) if chunks else 0} chunks")
                if chunks:
                    return "\n\n".join([str(chunk) for chunk in chunks[:top_k]])
            except Exception as e:
                print(f"  search() failed: {e}")

        # Method 2: Try query() method
        if hasattr(vector_store, 'query') and callable(vector_store.query):
            print(f"  Using vector_store.query()")
            try:
                result = vector_store.query(question, top_k=top_k)
                if isinstance(result, dict):
                    if 'sources' in result:
                        chunks = result['sources']
                    elif 'context' in result:
                        chunks = result['context']
                    elif 'answer' in result:
                        # If query returns answer directly, use it
                        return result['answer']
                    else:
                        chunks = []
                elif isinstance(result, list):
                    chunks = result
                else:
                    chunks = []

                print(f"  Query returned: {len(chunks)} chunks")
                if chunks:
                    return "\n\n".join([str(chunk) for chunk in chunks[:top_k]])
            except Exception as e:
                print(f"  query() failed: {e}")

        # Method 3: Try similarity_search() (common in FAISS, Chroma)
        if hasattr(vector_store, 'similarity_search') and callable(vector_store.similarity_search):
            print(f"  Using vector_store.similarity_search()")
            try:
                chunks = vector_store.similarity_search(question, k=top_k)
                print(f"  similarity_search returned: {len(chunks)} chunks")
                if chunks:
                    return "\n\n".join([str(chunk) for chunk in chunks[:top_k]])
            except Exception as e:
                print(f"  similarity_search() failed: {e}")

        # Method 4: If vector store has chunks directly
        if hasattr(vector_store, 'chunks') and vector_store.chunks:
            print(f"  Using vector_store.chunks directly")
            chunks = vector_store.chunks
            print(f"  Total chunks available: {len(chunks)}")

            # Simple keyword matching as fallback
            question_lower = question.lower()
            question_words = [w for w in question_lower.split() if len(w) > 3]

            relevant_chunks = []
            for chunk in chunks[:20]:  # Check first 20 chunks for performance
                chunk_lower = str(chunk).lower()
                matches = sum(1 for word in question_words if word in chunk_lower)
                if matches > 0:
                    relevant_chunks.append((matches, chunk))

            # Sort by number of matches
            relevant_chunks.sort(key=lambda x: x[0], reverse=True)

            # Take top chunks
            top_chunks = [chunk for _, chunk in relevant_chunks[:top_k]]
            print(f"  Found {len(top_chunks)} relevant chunks by keyword")

            if top_chunks:
                return "\n\n".join([str(chunk) for chunk in top_chunks])

        print(f"  WARNING: No context found using any method")
        return ""

    except Exception as e:
        print(f"  ERROR in build_rag_context: {e}")
        import traceback
        traceback.print_exc()
        return ""


def get_context_fallback(vector_store, question):
    """
    Alternative method to get context when main methods fail
    """
    try:
        # If vector store has any content, return first few chunks
        if hasattr(vector_store, 'chunks') and vector_store.chunks:
            print(f"  Fallback: Returning first 3 chunks")
            return "\n\n".join([str(chunk) for chunk in vector_store.chunks[:3]])

        # Try to get any content from vector store
        for attr in ['documents', 'texts', 'contents', 'data']:
            if hasattr(vector_store, attr):
                content = getattr(vector_store, attr)
                if content and len(content) > 0:
                    print(f"  Fallback: Found content in {attr}")
                    return "\n\n".join([str(item) for item in content[:3]])

        return ""
    except Exception as e:
        print(f"  Fallback error: {e}")
        return ""

# -------------------------
# Additional helper functions for Django views
# -------------------------

def get_workspace_status(workspace_id: str) -> dict:
    """Get status of a workspace"""
    ws = workspace_manager.get_workspace(workspace_id)
    if not ws:
        return {"error": "Workspace not found"}

    return {
        "workspace_id": ws.id,
        "status": getattr(ws, 'extraction_status', 'unknown'),
        "progress": getattr(ws, 'extraction_progress', 0),
        "files": getattr(ws, 'files', []),
        "has_vector_store": hasattr(ws, 'vector_store') and ws.vector_store is not None
    }


def list_all_workspaces() -> list:
    """List all workspaces"""
    # This assumes WorkspaceManager has a way to list workspaces
    # If not, we need to track them differently
    return []


workspaces = workspace_manager.list_workspaces()
if workspaces:
    ws_id = workspaces[0]["id"]
    ws = workspace_manager.get_workspace(ws_id)

    print(f"Workspace ID: {ws.id}")
    print(f"Status: {getattr(ws, 'extraction_status', 'N/A')}")

    if hasattr(ws, 'vector_store'):
        vs = ws.vector_store
        print(f"\nVector Store Info:")
        print(f"  Type: {type(vs)}")
        print(f"  Methods: {[m for m in dir(vs) if not m.startswith('_')]}")

        if hasattr(vs, 'chunks'):
            print(f"  Chunks: {len(vs.chunks)}")
            for i, chunk in enumerate(vs.chunks[:3]):
                print(f"  Chunk {i + 1}: {chunk[:200]}...")
        else:
            print("  No chunks attribute")
    else:
        print("No vector store found")
else:
    print("No workspaces found")