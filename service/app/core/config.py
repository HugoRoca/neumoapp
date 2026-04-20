from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://root:root@localhost:5432/neumoapp_db"
    
    # JWT
    SECRET_KEY: str = "neumoapp-secret-key-change-in-production-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Application
    PROJECT_NAME: str = "Neumoapp API"
    VERSION: str = "1.0.0"

    # OpenAI-compatible API (asistente POST /chat)
    # Nube: solo OPENAI_API_KEY + modelo OpenAI.
    # Local (Ollama): OPENAI_BASE_URL=http://localhost:11434/v1 y OPENAI_CHAT_MODEL=llama3.2 (p. ej.)
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: Optional[str] = None
    OPENAI_CHAT_MODEL: str = "gpt-4o-mini"
    # Hora de referencia para el asistente (qué es "hoy" y "ya pasó la mañana")
    APP_TIMEZONE: str = "America/Lima"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

