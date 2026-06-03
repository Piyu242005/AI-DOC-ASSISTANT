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

    def index_document(self, document_text: str, file_hash: str = None):
        """
        Chunks the document and stores it in the vector database incrementally.
        Yields progress updates: (progress_percent, message, is_cache_hit, total_chunks, time_taken)
        """
        start_time = time.time()

        # Use hash-based collection name if provided
        collection_name = f"doc_{file_hash}" if file_hash else "document_context"
        self.collection_name = collection_name

        # Check cache
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            count = self.collection.count()
            if count > 0:
                # Cache Hit!
                yield (
                    100,
                    "⚡ Document already indexed",
                    True,
                    count,
                    time.time() - start_time,
                )
                return
        except Exception:
            pass  # Collection does not exist

        # Cache Miss
        yield (10, "📖 Extracting Text...", False, 0, 0)

        try:
            self.client.delete_collection(self.collection_name)
        except Exception:
            pass

        self.collection = self.client.get_or_create_collection(
            name=self.collection_name
        )

        yield (25, "✂️ Creating Chunks...", False, 0, 0)

        chunks = self._chunk_text(document_text)
        total_chunks = len(chunks)
        if not chunks:
            yield (
                100,
                "❌ No text found in document.",
                False,
                0,
                time.time() - start_time,
            )
            return

        ids = [f"chunk_{i}" for i in range(total_chunks)]

        # Batch processing (100 chunks at a time)
        batch_size = 100
        for i in range(0, total_chunks, batch_size):
            batch_chunks = chunks[i : i + batch_size]
            batch_ids = ids[i : i + batch_size]

            # Scale progress from 25% to 95% during embedding
            progress_percent = 25 + int((i / total_chunks) * 70)
            yield (
                progress_percent,
                f"🧠 Generating Embeddings... ({min(i + batch_size, total_chunks)}/{total_chunks})",
                False,
                total_chunks,
                0,
            )

            # ChromaDB handles generating embeddings synchronously via all-MiniLM-L6-v2 here
            self.collection.add(documents=batch_chunks, ids=batch_ids)

        # Final success yield
        yield (
            100,
            "💾 Building Vector Index... 100%",
            False,
            total_chunks,
            time.time() - start_time,
        )

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
