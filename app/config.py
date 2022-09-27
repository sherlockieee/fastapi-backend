from typing import Optional
from pydantic import BaseSettings
import os
from dotenv import load_dotenv
from starlette.config import Config


class Settings(BaseSettings):
    load_dotenv()

    DATABASE_URL: str = os.getenv("DATABASE_URL")
    ENVIRONMENT: Optional[str] = os.getenv("ENVIRONMENT")

    SHOW_DOCS_ENVIRONMENT = ("local", "staging")

    class Config:
        case_sensitive = True


settings = Settings()
