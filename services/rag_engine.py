import time
from typing import Callable, Optional

import chromadb


class RAGManager:
    """
    Retrieval-Augmented Generation (RAG) engine for NeuraFlow AI.
    Handles document chunking, embeddings, and semantic search using ChromaDB.
    """

    def __init__(self, db_path="./chroma_db", collection_name="document_context"):
        self.client = chromadb.PersistentClient(path=db_path)
        self.default_collection_name = collection_name
        self.collection_name = collection_name
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name
        )

    def _chunk_text(
        self, text: str, chunk_size: int = 1500, overlap: int = 100
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

    def set_collection(self, collection_name: str):
        """Sets the active collection for indexing and retrieval."""
        self.collection_name = collection_name
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name
        )

    def is_indexed(self, doc_hash: str) -> bool:
        """Checks if a document with the given hash has already been indexed."""
        collection_name = f"doc_{doc_hash}"
        try:
            # Check if collection exists and has documents
            coll = self.client.get_collection(name=collection_name)
            return coll.count() > 0
        except Exception:
            return False

    def index_document(
        self,
        document_text: str,
        doc_hash: Optional[str] = None,
        metadata: Optional[dict] = None,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> dict:
        """
        Chunks the document and stores it in the vector database.
        Returns metrics dictionary.
        """
        start_time = time.time()

        if doc_hash:
            self.collection_name = f"doc_{doc_hash}"
        else:
            self.collection_name = self.default_collection_name
            # Reset default collection
            try:
                self.client.delete_collection(self.collection_name)
            except Exception:
                pass

        self.collection = self.client.get_or_create_collection(
            name=self.collection_name
        )

        if progress_callback:
            progress_callback("📖 Extracting Text...", 20)

        if progress_callback:
            progress_callback("✂️ Creating Chunks...", 40)

        chunks = self._chunk_text(document_text)
        if not chunks:
            return {"chunks": 0, "embeddings": 0, "time": 0.0, "cache_hit": False}

        if progress_callback:
            progress_callback("🧠 Generating Embeddings...", 70)

        # Create unique IDs for each chunk
        ids = [f"chunk_{i}" for i in range(len(chunks))]

        # Attach metadata to each chunk
        metadatas = [metadata] * len(chunks) if metadata else None

        if progress_callback:
            progress_callback("💾 Building Vector Index...", 90)

        # Add to ChromaDB (automatically uses all-MiniLM-L6-v2 embeddings)
        self.collection.add(documents=chunks, ids=ids, metadatas=metadatas)

        index_time = time.time() - start_time

        if progress_callback:
            progress_callback("✅ Ready for Search", 100)

        return {
            "chunks": len(chunks),
            "embeddings": len(chunks),
            "time": index_time,
            "cache_hit": False,
        }

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
