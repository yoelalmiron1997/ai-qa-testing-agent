import os

try:
    from pydantic_settings import BaseSettings
except Exception:
    try:
        from pydantic.v1 import BaseSettings
    except Exception:
        from pydantic import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI QA Testing Agent"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./ai_qa_agent.db")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    class Config:
        case_sensitive = True

settings = Settings()
