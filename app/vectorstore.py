from typing import Any


class VectorStore:
    collection_name = "properties"

    def __init__(self, path: str):
        import chromadb
        self.client = chromadb.PersistentClient(path=path)
        self.collection = self.client.get_or_create_collection(
            self.collection_name, metadata={"hnsw:space": "cosine"}
        )

    def upsert(self, ids: list[str], documents: list[str], embeddings: list[list[float]],
               metadatas: list[dict[str, Any]]) -> None:
        self.collection.upsert(ids=ids, documents=documents, embeddings=embeddings,
                               metadatas=metadatas)

    def count(self) -> int:
        return self.collection.count()

    def query(self, embedding: list[float], n_results: int = 10) -> list[dict[str, Any]]:
        result = self.collection.query(query_embeddings=[embedding], n_results=n_results)
        ids = result.get("ids", [[]])[0]
        distances = result.get("distances", [[]])[0]
        docs = result.get("documents", [[]])[0]
        metadata = result.get("metadatas", [[]])[0]
        if isinstance(metadata, dict):
            metadata = [metadata]
        return [{"id": str(i), "score": max(0.0, 1.0 - float(d)),
                 "document": doc, "metadata": meta or {}}
                for i, d, doc, meta in zip(ids, distances, docs, metadata)]
