from app import db
from app.db import engine, SessionLocal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

db.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "https://capstone-exploration.vercel.app",
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    try:
        db = SessionLocal()
        yield db
    except Exception as e:
        raise e
    finally:
        db.close()


from app.api.api import router

app.include_router(router)
