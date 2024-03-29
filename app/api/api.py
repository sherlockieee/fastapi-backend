from fastapi import APIRouter

from app.api.endpoints import projects, tags, user, transactions, refunds, payouts

router = APIRouter()
router.include_router(projects.router)
router.include_router(tags.router)
router.include_router(user.router)
router.include_router(transactions.router)
router.include_router(refunds.router)
router.include_router(payouts.router)


@router.get("/")
async def root():
    return {"message": "Hello World, from FastAPI"}
