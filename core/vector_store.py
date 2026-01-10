import faiss
import numpy as np
from numpy.ma.core import indices
from sentence_transformers import SentenceTransformer

class VectorStore:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.text_chunks = []

    def build_index(self, chunks: list[str]):
        emmbeddings = self.model.encode(chunks, convert_to_numpy=True)
        dim = emmbeddings.shape[1]

        self.index = faiss.IndexFlatL2(dim)
        self.index.add(emmbeddings)

        self.text_chunks = chunks

    def search(self, querry: str, k: int = 4) -> list[str]:
        query_embedding = self.model.encode(querry, convert_to_numpy=True)
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)

        distances, indices = self.index.search(query_embedding, k)

        return [self.text_chunks[i] for i in indices[0]]