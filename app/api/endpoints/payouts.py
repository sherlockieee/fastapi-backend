from typing import List, Union
from fastapi import APIRouter, Depends, status, HTTPException, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session, joinedload, contains_eager


import app.models as models
from app.api.deps import get_current_active_user, get_db
import app.schemas.payout as schema
from app.schemas.transaction_status import TransactionStatus
from app.schemas.project_status import ProjectStatus
from app.schemas.currency import Currency


router = APIRouter(prefix="/payouts", tags=["transactions"])


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[schema.PayoutOut])
def get_payouts(db: Session = Depends(get_db)):
    all_payouts = db.query(models.Payout).all()
    return all_payouts


@router.get("/project/{project_id}", response_model=List[schema.PayoutOut])
def get_payout_for_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    payout = (
        db.query(models.Payout)
        .join(models.Payout.project)
        .join(models.Payout.user)
        .options(contains_eager(models.Payout.user))
        .options(contains_eager(models.Payout.project))
        .filter(models.Project.id == project_id)
        .filter(models.User.id == current_user.id)
        .first()
    )

    return payout


@router.post(
    "/{project_id}",
    status_code=status.HTTP_201_CREATED,
    response_model=List[schema.PayoutOut],
)
async def payout_project(
    background_tasks: BackgroundTasks,
    project_id: int,
    db: Session = Depends(get_db),
):

    project: models.Project = (
        db.query(models.Project)
        .options(
            joinedload(models.Project.users).options(
                joinedload(models.Transaction.user)
            )
        )
        .filter(models.Project.id == project_id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    elif project.status != ProjectStatus.SUCCESS:
        raise HTTPException(
            status_code=404, detail="Project is not successful so payout cannot happen"
        )

    all_transactions: List[models.Transaction] = (
        db.query(models.Transaction)
        .filter(models.Transaction.project_id == project_id)
        .filter(models.Transaction.status == TransactionStatus.SUCCESS)
        .all()
    )

    currency_payout_dict = {}
    for cur in Currency:
        total_payout = sum(
            [
                transaction.amount
                for transaction in all_transactions
                if transaction.currency == cur
            ]
        )
        currency_payout_dict[cur] = total_payout

        payout = models.Payout(
            amount=total_payout,
            currency=cur,
            user_id=project.owner.id,
            project_id=project_id,
            status=TransactionStatus.SUCCESS,
        )

        try:
            db.add(payout)
            # send_email_when_refund_success(background_tasks, project, user_id)
            print("payout successfully")
            db.commit()
        except Exception as error:
            print(error)
            payout.status = TransactionStatus.PENDING

    all_payouts = (
        db.query(models.Payout)
        .filter(models.Transaction.project_id == project_id)
        .all()
    )

    return all_payouts
