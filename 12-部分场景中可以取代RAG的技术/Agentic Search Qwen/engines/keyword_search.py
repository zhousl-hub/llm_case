from __future__ import annotations
import json
import os
from typing import List, Dict, Optional
from whoosh.index import create_in, exists_in, open_dir
from whoosh.fields import Schema, TEXT, ID, KEYWORD, STORED
from whoosh.qparser import MultifieldParser, OrGroup
from whoosh.analysis import SimpleAnalyzer
from config import KEYWORD_INDEX_DIR

try:
    import jieba as _jieba
    HAS_JIEBA = True
except ImportError:
    HAS_JIEBA = False


def _tokenize_chinese(text: str) -> str:
    if HAS_JIEBA and text:
        return " ".join(_jieba.cut_for_search(text))
    return text


class KeywordSearchEngine:
    def __init__(self):
        self.index_dir = KEYWORD_INDEX_DIR
        self.indexes = {}
        self._analyzer = SimpleAnalyzer()

    def _get_schema(self) -> Schema:
        return Schema(
            doc_id=ID(stored=True, unique=True),
            title=TEXT(analyzer=self._analyzer, stored=True),
            content=TEXT(analyzer=self._analyzer, stored=True),
            category=KEYWORD(stored=True),
            source=TEXT(stored=True),
        )

    def _get_index(self, index_name: str):
        if index_name in self.indexes:
            return self.indexes[index_name]

        index_path = os.path.join(self.index_dir, index_name)
        os.makedirs(index_path, exist_ok=True)

        if exists_in(index_path):
            ix = open_dir(index_path)
        else:
            ix = create_in(index_path, self._get_schema())

        self.indexes[index_name] = ix
        return ix

    def add_documents(self, index_name: str, documents: list[dict]):
        ix = self._get_index(index_name)
        writer = ix.writer()

        for i, doc in enumerate(documents):
            title = _tokenize_chinese(doc.get("title", ""))
            content = _tokenize_chinese(doc.get("content", ""))
            doc_id = doc.get("id", f"{index_name}_{i}")
            writer.update_document(
                doc_id=doc_id,
                title=title,
                content=content,
                category=doc.get("category", ""),
                source=doc.get("source", ""),
            )

        writer.commit()
        return len(documents)

    def search(self, query: str, index_name: str = None,
               fields: list[str] = None, limit: int = 10) -> str:
        if fields is None:
            fields = ["title", "content"]

        tokenized_query = _tokenize_chinese(query)

        if index_name:
            return self._search_single(index_name, tokenized_query, fields, limit)
        else:
            all_results = {}
            for name in self.list_indexes():
                result = self._search_single(name, tokenized_query, fields, limit)
                parsed = json.loads(result)
                if parsed.get("results"):
                    all_results[name] = parsed["results"]
            return json.dumps({"results": all_results}, ensure_ascii=False, indent=2)

    def _search_single(self, index_name: str, query: str,
                       fields: list[str], limit: int) -> str:
        try:
            ix = self._get_index(index_name)
        except Exception:
            return json.dumps({"error": f"Index '{index_name}' not found"},
                              ensure_ascii=False)

        try:
            searcher = ix.searcher()
            parser = MultifieldParser(fields, ix.schema)
            parsed_query = parser.parse(query)
            results = searcher.search(parsed_query, limit=limit)

            formatted = []
            for hit in results:
                formatted.append({
                    "doc_id": hit.get("doc_id", ""),
                    "title": hit.get("title", ""),
                    "content": hit.get("content", "")[:500],
                    "category": hit.get("category", ""),
                    "source": hit.get("source", ""),
                    "score": round(hit.score, 4)
                })

            searcher.close()
            return json.dumps({
                "index": index_name,
                "query": query,
                "total_found": len(results),
                "results": formatted
            }, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    def list_indexes(self) -> list[str]:
        indexes = []
        if os.path.exists(self.index_dir):
            for name in os.listdir(self.index_dir):
                index_path = os.path.join(self.index_dir, name)
                if os.path.isdir(index_path) and exists_in(index_path):
                    indexes.append(name)
        return indexes

    def get_index_info(self, index_name: str) -> str:
        try:
            ix = self._get_index(index_name)
            return json.dumps({
                "name": index_name,
                "document_count": ix.doc_count()
            }, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    def get_all_indexes_info(self) -> str:
        infos = {}
        for name in self.list_indexes():
            infos[name] = json.loads(self.get_index_info(name))
        return json.dumps(infos, ensure_ascii=False, indent=2)
