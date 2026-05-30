"""聊天服务测试"""
import pytest
from unittest.mock import patch, MagicMock
from services.chat_service import ChatService

def test_chat():
    with patch("services.chat_service.OpenAI") as mock_openai:
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "你好！有什么可以帮助你的？"
        mock_openai.return_value.chat.completions.create.return_value = mock_response

        service = ChatService()
        result = service.chat("你好")
        assert result == "你好！有什么可以帮助你的？"
