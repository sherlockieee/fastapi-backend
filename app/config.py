from typing import Optional
from pydantic import BaseSettings, EmailStr
import os
from dotenv import load_dotenv


class Settings(BaseSettings):
    load_dotenv()

    DATABASE_URL: str
    ENVIRONMENT: Optional[str]

    SHOW_DOCS_ENVIRONMENT = ("local", "staging")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 30  # 30 minutes
    ALGORITHM = "HS256"
    JWT_SECRET_KEY: str
    JWT_REFRESH_SECRET_KEY: str

    EMAIL_HOST: str
    EMAIL_PORT: int
    EMAIL_USERNAME: str
    EMAIL_PASSWORD: str
    EMAIL_FROM: EmailStr

    class Config:
        case_sensitive = True
        env_file = "./.env"


settings = Settings()
