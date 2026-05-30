"""搜索数据模式"""
from pydantic import BaseModel
from typing import Optional

class SearchRequest(BaseModel):
    query: str
    index: str = "default"
    size: int = 10

class SearchResponse(BaseModel):
    results: dict
