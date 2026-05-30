"""Redis工具"""
import redis
from config import settings

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

class CacheManager:
    def __init__(self, prefix: str = "cache", default_ttl: int = 3600):
        self.prefix = prefix
        self.default_ttl = default_ttl

    def get(self, key: str) -> str:
        return redis_client.get(f"{self.prefix}:{key}")

    def set(self, key: str, value: str, ttl: int = None):
        redis_client.setex(f"{self.prefix}:{key}", ttl or self.default_ttl, value)

    def delete(self, key: str):
        redis_client.delete(f"{self.prefix}:{key}")

    def exists(self, key: str) -> bool:
        return redis_client.exists(f"{self.prefix}:{key}")

cache = CacheManager()
