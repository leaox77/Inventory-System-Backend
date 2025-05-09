from pydantic_settings import BaseSettings
from pydantic import PostgresDsn

class Settings(BaseSettings):
    DATABASE_URL: PostgresDsn
    SECRET_KEY: str
    ALGORITHM: str = "HS256"  # ✅ Agregado
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # ✅ Agregado
    API_V1_STR: str = "/api/v1"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
