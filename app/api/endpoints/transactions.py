import json
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy import insert


import app.models as models
from app.api.deps import get_current_active_user, get_current_user, get_db
import app.schemas.transaction as schema
from app.schemas.backer_status import BackerStatus

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=schema.TransactionOut
)
def create_transaction(
    transaction: schema.TransactionIn,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    transaction_dict = jsonable_encoder(transaction)

    project = (
        db.query(models.Project)
        .filter(models.Project.id == transaction.project_id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    print(project.total_credits)
    print(project.credits_sold)
    print(transaction_dict["quantity"])
    if (project.total_credits - project.credits_sold) < transaction_dict["quantity"]:
        raise HTTPException(
            status_code=404, detail="Buying more credits than is available."
        )

    # new_transaction = models.BackerProjectOrder(
    #     **transaction_dict, backer_id=current_user.id, status=BackerStatus.SUCCESS
    # )
    new_transaction = models.BackerProjectOrder(
        **transaction_dict, backer_id=current_user.id, status=BackerStatus.SUCCESS
    )
    db.add(new_transaction)
    project.credits_sold += transaction_dict["quantity"]
    project.total_raised += transaction_dict["amount"]
    project.total_backers += 1

    db.commit()
    db.refresh(new_transaction)

    return new_transaction
