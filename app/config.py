from pydantic import BaseSettings

import os
from dotenv import load_dotenv


class Settings(BaseSettings):
    load_dotenv()

    DATABASE_URL: str = os.getenv("DATABASE_URL")
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    class Config:
        case_sensitive = True


settings = Settings()
