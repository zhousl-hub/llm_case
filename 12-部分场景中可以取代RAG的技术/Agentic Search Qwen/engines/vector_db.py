from __future__ import annotations
import json
from typing import List, Dict, Optional
import chromadb
from config import VECTOR_DB_DIR


class VectorDBEngine:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=VECTOR_DB_DIR)
        self.collections = {}

    def _get_collection(self, name: str):
        if name not in self.collections:
            self.collections[name] = self.client.get_or_create_collection(
                name=name,
                metadata={"hnsw:space": "cosine"}
            )
        return self.collections[name]

    def add_documents(self, collection_name: str, documents: list[str],
                      metadatas: list[dict] = None, ids: list[str] = None):
        collection = self._get_collection(collection_name)
        if ids is None:
            existing_count = collection.count()
            ids = [f"{collection_name}_{existing_count + i}" for i in range(len(documents))]
        if metadatas is None:
            metadatas = [{"source": collection_name} for _ in range(len(documents))]

        batch_size = 100
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i + batch_size]
            batch_ids = ids[i:i + batch_size]
            batch_meta = metadatas[i:i + batch_size]
            collection.add(
                documents=batch_docs,
                ids=batch_ids,
                metadatas=batch_meta
            )

        return len(documents)

    def search(self, query: str, collection_name: str = None,
               n_results: int = 5, where: dict = None) -> str:
        if collection_name:
            try:
                collection = self._get_collection(collection_name)
            except Exception:
                return json.dumps({"error": f"Collection '{collection_name}' not found"},
                                  ensure_ascii=False)

            query_params = {"query_texts": [query], "n_results": n_results}
            if where:
                query_params["where"] = where

            results = collection.query(**query_params)
            return self._format_results(results, collection_name)
        else:
            all_results = {}
            for name in self.list_collections():
                try:
                    collection = self._get_collection(name)
                    query_params = {"query_texts": [query], "n_results": n_results}
                    results = collection.query(**query_params)
                    formatted = self._format_results(results, name)
                    parsed = json.loads(formatted)
                    if parsed.get("results"):
                        all_results[name] = parsed["results"]
                except Exception:
                    continue

            return json.dumps({"results": all_results}, ensure_ascii=False, indent=2)

    def _format_results(self, results: dict, collection_name: str) -> str:
        formatted = []
        if results and results.get("documents") and results["documents"][0]:
            docs = results["documents"][0]
            distances = results.get("distances", [[]])[0] if results.get("distances") else [0] * len(docs)
            metadatas = results.get("metadatas", [[]])[0] if results.get("metadatas") else [{}] * len(docs)
            ids = results.get("ids", [[]])[0] if results.get("ids") else [""] * len(docs)

            for doc, dist, meta, doc_id in zip(docs, distances, metadatas, ids):
                formatted.append({
                    "id": doc_id,
                    "content": doc,
                    "distance": round(dist, 4),
                    "metadata": meta
                })

        return json.dumps({
            "collection": collection_name,
            "results": formatted
        }, ensure_ascii=False, indent=2)

    def list_collections(self) -> list[str]:
        return [c.name for c in self.client.list_collections()]

    def get_collection_info(self, collection_name: str) -> str:
        try:
            collection = self._get_collection(collection_name)
            count = collection.count()
            peek = collection.peek(limit=3)
            return json.dumps({
                "name": collection_name,
                "document_count": count,
                "sample_documents": peek.get("documents", [[]])[0] if peek.get("documents") else []
            }, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    def get_all_collections_info(self) -> str:
        infos = {}
        for name in self.list_collections():
            infos[name] = json.loads(self.get_collection_info(name))
        return json.dumps(infos, ensure_ascii=False, indent=2)
