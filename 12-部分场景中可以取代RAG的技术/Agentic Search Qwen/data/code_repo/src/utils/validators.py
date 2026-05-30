"""数据验证工具"""
import re
from typing import Optional

def validate_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    pattern = r"^1[3-9]\d{9}$"
    return bool(re.match(pattern, phone))

def validate_password(password: str) -> Optional[str]:
    if len(password) < 8:
        return "密码长度不能少于8位"
    if not re.search(r"[A-Z]", password):
        return "密码必须包含大写字母"
    if not re.search(r"[a-z]", password):
        return "密码必须包含小写字母"
    if not re.search(r"\d", password):
        return "密码必须包含数字"
    return None

def sanitize_input(text: str) -> str:
    text = re.sub(r"<[^>]*>", "", text)
    text = re.sub(r"["';]", "", text)
    return text.strip()
