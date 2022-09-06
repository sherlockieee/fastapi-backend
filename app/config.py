from pydantic import BaseSettings
import os
from dotenv import load_dotenv


class Settings(BaseSettings):
    load_dotenv()

    DATABASE_URL: str = os.getenv("DATABASE_URL")

    class Config:
        case_sensitive = True


settings = Settings()
