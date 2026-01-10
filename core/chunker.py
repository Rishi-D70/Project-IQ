class TextChunker:

    def __init__(self, chunk_size = 600, overlap = 100):
        if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk size")

        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        chunks = []
        start = 0
        lenght = len(text)

        while start < lenght:
            end = start + self.chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - self.overlap

        return chunks

