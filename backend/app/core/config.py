# ✅ new
from pydantic_settings import BaseSettings
# 👇 ADDED: Import ConfigDict to replace the inner Config class
from pydantic import ConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Inventory Storage Management"
    DATABASE_URL: str = "postgresql+asyncpg://akshay:password123@localhost:5432/inventory_db"
    JWT_SECRET: str = "change-this-secret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    THRESHOLD_LOOKBACK_DAYS: int = 14
    LEAD_TIME_DAYS: int = 2
    SAFETY_FACTOR: float = 1.25

    # 👇 FIXED: Replaced deprecated inner Config class with model_config
    model_config = ConfigDict(env_file = ".env")


settings = Settings()