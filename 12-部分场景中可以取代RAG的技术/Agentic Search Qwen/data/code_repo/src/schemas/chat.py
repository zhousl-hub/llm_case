"""聊天数据模式"""
from pydantic import BaseModel
from typing import Optional, List

class ChatRequest(BaseModel):
    message: str
    knowledge: Optional[str] = None
    history: Optional[List[dict]] = None

class ChatResponse(BaseModel):
    answer: str
