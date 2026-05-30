"""路由注册"""
from fastapi import APIRouter
from routers.user_router import user_router
from routers.project_router import project_router
from routers.chat_router import chat_router
from routers.search_router import search_router

api_router = APIRouter()
api_router.include_router(user_router, prefix="/users", tags=["users"])
api_router.include_router(project_router, prefix="/projects", tags=["projects"])
api_router.include_router(chat_router, prefix="/chat", tags=["chat"])
api_router.include_router(search_router, prefix="/search", tags=["search"])
