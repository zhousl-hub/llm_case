"""搜索路由"""
from fastapi import APIRouter
from services.search_service import SearchService
from schemas.search import SearchRequest, SearchResponse

search_router = APIRouter()

@search_router.post("/", response_model=SearchResponse)
def search(request: SearchRequest):
    service = SearchService()
    result = service.search(
        index=request.index,
        query=request.query,
        size=request.size
    )
    return SearchResponse(results=result)
