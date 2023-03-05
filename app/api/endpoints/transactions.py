from typing import List
from fastapi import APIRouter, Depends, status, HTTPException, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session, contains_eager, joinedload


import app.models as models
from app.api.deps import get_current_active_user, get_db
from app.models.transactions import Transaction
import app.schemas.transaction as schema
from app.schemas.transaction_status import TransactionStatus, TransactionType
from app.schemas.project_status import ProjectStatus
from app.utils.emails import (
    send_email_when_funding_reaches,
    send_email_when_transaction_succeeds,
)

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("/", status_code=200, response_model=List[schema.TransactionOut])
def get_transactions(
    db: Session = Depends(get_db),
):
    transactions = (
        db.query(Transaction)
        .options(joinedload(Transaction.user))
        .options(joinedload(Transaction.project))
        # .join(Transaction.refund)
        .all()
    )

    return transactions


@router.get("/project/{project_id}", response_model=List[schema.TransactionOut])
def get_transactions_for_one_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    transactions = (
        db.query(Transaction)
        .join(Transaction.project)
        .join(Transaction.user)
        .options(contains_eager(Transaction.user))
        .options(contains_eager(Transaction.project))
        .filter(models.Project.id == project_id)
        .filter(models.User.id == current_user.id)
        .all()
    )

    return transactions


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=schema.TransactionOut
)
async def create_transaction(
    background_tasks: BackgroundTasks,
    transaction: schema.TransactionIn,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    transaction_dict = jsonable_encoder(transaction)

    project = (
        db.query(models.Project)
        .options(
            joinedload(models.Project.users).options(
                joinedload(models.Transaction.user)
            )
        )
        .filter(models.Project.id == transaction.project_id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.status != ProjectStatus.IN_FUNDING:
        raise HTTPException(status_code=404, detail="Project is no longer in funding")

    if (project.total_credits - project.credits_sold) < transaction_dict["quantity"]:
        raise HTTPException(
            status_code=404, detail="Buying more credits than is available."
        )

    new_transaction = models.Transaction(
        **transaction_dict,
        user_id=current_user.id,
        status=TransactionStatus.SUCCESS,
    )
    db.add(new_transaction)
    project.credits_sold += transaction_dict["quantity"]
    project.total_raised += transaction_dict["amount"]

    try:
        send_email_when_transaction_succeeds(
            background_tasks, transaction_dict, project.owner, current_user
        )
    except Exception as error:
        print(error)
        new_transaction.status = TransactionStatus.PENDING

    if project.credits_sold == project.total_credits:
        project.status = ProjectStatus.SUCCESS
        try:
            send_email_when_funding_reaches(background_tasks, project)
        except Exception as error:
            print(error)

    db.commit()

    transaction = (
        db.query(Transaction)
        .options(joinedload(Transaction.user))
        .options(joinedload(Transaction.project))
        .where(Transaction.id == new_transaction.id)
        .one()
    )

    return transaction
