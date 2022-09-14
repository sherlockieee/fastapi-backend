from fastapi import APIRouter

from app.api.endpoints import projects

router = APIRouter()
router.include_router(projects.router, prefix="/projects", tags=["projects"])
# router.include_router(tags.router, prefix="/tags", tags=["tags"])


@router.get("/")
async def root():
    return {"message": "Hello World, from FastAPI"}
