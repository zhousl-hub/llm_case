"""搜索服务"""
from typing import List, Optional
from elasticsearch import Elasticsearch
from config import settings

class SearchService:
    def __init__(self):
        self.es = Elasticsearch(settings.ES_HOSTS)

    def search(self, index: str, query: str, size: int = 10) -> dict:
        body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["title^3", "content"],
                    "type": "best_fields",
                    "fuzziness": "AUTO"
                }
            },
            "highlight": {
                "fields": {
                    "title": {},
                    "content": {"fragment_size": 150}
                }
            }
        }
        return self.es.search(index=index, body=body, size=size)

    def suggest(self, index: str, prefix: str) -> List[str]:
        body = {
            "suggest": {
                "title-suggest": {
                    "prefix": prefix,
                    "completion": {"field": "title.suggest", "size": 5}
                }
            }
        }
        result = self.es.search(index=index, body=body)
        return [item["text"] for item in result["suggest"]["title-suggest"][0]["options"]]
