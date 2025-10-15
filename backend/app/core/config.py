from pydantic import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Inventory Storage Management"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/inventory_db"
    JWT_SECRET: str = "change-this-secret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    THRESHOLD_LOOKBACK_DAYS: int = 14
    LEAD_TIME_DAYS: int = 2
    SAFETY_FACTOR: float = 1.25


    class Config:
        env_file = ".env"


settings = Settings()