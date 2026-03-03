from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "NEXUS SOC Command Center"
    jwt_secret: str = "change-me-in-prod"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 120
    ollama_url: str = "http://ollama:11434"
    redis_url: str = "redis://redis:6379/0"


settings = Settings()
