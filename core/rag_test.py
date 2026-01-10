from core.ingest import ingest_document
from core.rag_query import RAGQueryEngine

# 1️⃣ Ingest ONCE
vector_store = ingest_document("MASTER SERVICES AGREEMENT.pdf")

# 2️⃣ Create RAG engine
rag = RAGQueryEngine(vector_store)

# 3️⃣ Ask questions (FAST)
while True:
    querry = input("Enter your qurey")
    print(rag.answer(querry))
#print(rag.answer("What is the termination notice period?"))
#print(rag.answer("What is the governing law?"))
#print(rag.answer("Who is the service provider?"))
