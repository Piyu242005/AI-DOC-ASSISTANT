import time

import chromadb


class RAGManager:
    """
    Retrieval-Augmented Generation (RAG) engine for NeuraFlow AI.
    Handles document chunking, embeddings, and semantic search using ChromaDB.
    """

    def __init__(self, db_path="./chroma_db", collection_name="document_context"):
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection_name = collection_name
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name
        )

    def _chunk_text(
        self, text: str, chunk_size: int = 1000, overlap: int = 200
    ) -> list:
        """Splits text into chunks of specified size with overlap."""
        chunks = []
        start = 0
        text_length = len(text)
        while start < text_length:
            end = min(start + chunk_size, text_length)
            chunks.append(text[start:end])
            if end == text_length:
                break
            start = start + chunk_size - overlap
        return chunks

    def index_document(self, document_text: str) -> int:
        """
        Chunks the document and stores it in the vector database.
        Resets the collection for a fresh document session.
        """
        # Reset collection for the new document
        try:
            self.client.delete_collection(self.collection_name)
        except Exception:
            pass
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name
        )

        chunks = self._chunk_text(document_text)
        if not chunks:
            return 0

        # Create unique IDs for each chunk
        ids = [f"chunk_{i}" for i in range(len(chunks))]

        # Add to ChromaDB (automatically uses all-MiniLM-L6-v2 embeddings)
        self.collection.add(documents=chunks, ids=ids)
        return len(chunks)

    def retrieve_context(self, query: str, k: int = 5):
        """
        Retrieves the top-k most relevant chunks for a given query.
        Returns (context_string, similarity_score, retrieval_time_seconds, num_chunks).
        """
        start_time = time.time()

        # Query ChromaDB
        results = self.collection.query(query_texts=[query], n_results=k)

        retrieval_time = time.time() - start_time

        # Check if we got results
        if not results["documents"] or not results["documents"][0]:
            return "", 0.0, retrieval_time, 0

        retrieved_chunks = results["documents"][0]
        distances = (
            results["distances"][0]
            if "distances" in results and results["distances"]
            else []
        )

        # Calculate a pseudo similarity score from L2 distances
        # Chroma default is squared L2. Lower is more similar.
        if distances:
            avg_distance = sum(distances) / len(distances)
            similarity_score = 1.0 / (1.0 + avg_distance)
        else:
            similarity_score = 0.0

        context_str = "\n\n---\n\n".join(retrieved_chunks)
        return context_str, similarity_score, retrieval_time, len(retrieved_chunks)
