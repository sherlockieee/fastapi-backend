from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

app_configs = {}
if settings.ENVIRONMENT not in settings.SHOW_DOCS_ENVIRONMENT:
    app_configs["openapi_url"] = None

app = FastAPI(**app_configs)

origins = [
    "https://capstone-exploration.vercel.app",
    "https://x-kickstarter-for-climate.vercel.app/",
    "http://localhost",
    "http://localhost:3000",
    "https://checkout.stripe.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from app.api.api import router

app.include_router(router)
