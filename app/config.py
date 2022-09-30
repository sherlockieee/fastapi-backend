from typing import Optional
from pydantic import BaseSettings
import os
from dotenv import load_dotenv


class Settings(BaseSettings):
    load_dotenv()

    DATABASE_URL: str = os.getenv("DATABASE_URL")
    ENVIRONMENT: Optional[str] = os.getenv("ENVIRONMENT")

    SHOW_DOCS_ENVIRONMENT = ("local", "staging")
    ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
    REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
    ALGORITHM = "HS256"
    SECRET_KEY = os.environ["JWT_SECRET_KEY"]
    REFRESH_SECRET_KEY = os.environ["JWT_REFRESH_SECRET_KEY"]

    class Config:
        case_sensitive = True


settings = Settings()
