from core.llm_client import OllamaClient
from core.llm_client import OllamaClient
import traceback


class RAGQueryEngine:
    def __init__(self, vector_store):
        self.vector_store = vector_store
        self.llm = OllamaClient()
        print(f"DEBUG: RAGQueryEngine initialized with vector_store type: {type(vector_store)}")

    def answer(self, question: str) -> str:
        print(f"DEBUG: Answering question: {question}")

        try:
            # Try different search methods
            relevant_chunks = []

            # Method 1: Try search() method
            if hasattr(self.vector_store, 'search') and callable(self.vector_store.search):
                print("DEBUG: Using vector_store.search()")
                relevant_chunks = self.vector_store.search(question, k=4)

            # Method 2: Try query() method (common in vector stores)
            elif hasattr(self.vector_store, 'query') and callable(self.vector_store.query):
                print("DEBUG: Using vector_store.query()")
                result = self.vector_store.query(question, top_k=4)
                if isinstance(result, dict) and 'sources' in result:
                    relevant_chunks = result['sources']
                elif isinstance(result, list):
                    relevant_chunks = result
                else:
                    relevant_chunks = []

            # Method 3: Try similarity_search() (common in FAISS, Chroma)
            elif hasattr(self.vector_store, 'similarity_search') and callable(self.vector_store.similarity_search):
                print("DEBUG: Using vector_store.similarity_search()")
                relevant_chunks = self.vector_store.similarity_search(question, k=4)

            # Method 4: If vector store has chunks directly
            elif hasattr(self.vector_store, 'chunks') and self.vector_store.chunks:
                print("DEBUG: Using vector_store.chunks directly")
                # Simple keyword matching as fallback
                question_lower = question.lower()
                relevant_chunks = [
                    chunk for chunk in self.vector_store.chunks[:10]  # Check first 10 chunks
                    if any(word in chunk.lower() for word in question_lower.split())
                ][:4]  # Take top 4
            else:
                print("DEBUG: No search method found in vector_store")
                relevant_chunks = []

            print(f"DEBUG: Found {len(relevant_chunks)} relevant chunks")

            if relevant_chunks:
                for i, chunk in enumerate(relevant_chunks[:2]):  # Show first 2 chunks
                    print(f"DEBUG: Chunk {i + 1}: {chunk[:200]}...")

            context = "\n\n".join(relevant_chunks) if relevant_chunks else ""

            if not context:
                print("DEBUG: No context found - returning fallback")
                return "The contract document has been processed but I couldn't find specific information to answer your question. Please try asking about general contract terms like 'What is this contract about?' or 'Who are the parties?'"

            prompt = f"""
You are a legal contract assistant. Answer the question ONLY using the context below.
If the answer cannot be determined from the context, say "The contract doesn't specify this clearly."

Context from contract:
{context}

Question:
{question}

Answer based only on the contract context above. Be specific and always cite relevant details:
"""

            print(f"DEBUG: Sending prompt to LLM (context length: {len(context)})")
            answer = self.llm.ask(prompt)
            print(f"DEBUG: LLM response: {answer[:200]}...")

            return answer

        except Exception as e:
            print(f"ERROR in RAGQueryEngine.answer: {str(e)}")
            traceback.print_exc()
            return f"Error processing query: {str(e)}"