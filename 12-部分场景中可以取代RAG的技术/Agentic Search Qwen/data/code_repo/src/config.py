"""应用配置"""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "CloudEngine"
    DATABASE_URL: str = "mysql://root:password@localhost:3306/cloudengine"
    REDIS_URL: str = "redis://localhost:6379/0"
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    SECRET_KEY: str = "your-secret-key"
    DEBUG: bool = False
    class Config:
        env_file = ".env"

settings = Settings()
