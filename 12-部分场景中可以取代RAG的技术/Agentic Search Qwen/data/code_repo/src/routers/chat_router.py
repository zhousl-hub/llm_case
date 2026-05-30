"""聊天路由"""
from fastapi import APIRouter
from services.chat_service import ChatService
from schemas.chat import ChatRequest, ChatResponse

chat_router = APIRouter()

@chat_router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest):
    service = ChatService()
    answer = service.chat_with_knowledge(
        message=request.message,
        knowledge=request.knowledge,
        history=request.history
    )
    return ChatResponse(answer=answer)
