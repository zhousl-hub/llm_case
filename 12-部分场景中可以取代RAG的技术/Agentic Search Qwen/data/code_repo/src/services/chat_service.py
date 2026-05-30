"""智能客服服务"""
from typing import List, Optional
from openai import OpenAI
from config import settings

class ChatService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.SECRET_KEY)
        self.model = "qwen3.6-plus"

    def chat(self, message: str, history: List[dict] = None) -> str:
        messages = history or []
        messages.append({"role": "user", "content": message})
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
        )
        return response.choices[0].message.content

    def chat_with_knowledge(self, message: str, knowledge: str,
                           history: List[dict] = None) -> str:
        system_prompt = f"""你是一个智能客服助手。请根据以下知识库内容回答用户问题。
如果知识库中没有相关信息，请诚实说明。
知识库内容：{knowledge}"""
        messages = [{"role": "system", "content": system_prompt}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": message})
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.3,
        )
        return response.choices[0].message.content
