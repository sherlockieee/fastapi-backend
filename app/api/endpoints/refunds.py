from typing import List
from fastapi import APIRouter, Depends, status, HTTPException, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session, joinedload


import app.models as models
from app.api.deps import get_current_active_user, get_db
import app.schemas.refund as schema
from app.schemas.transaction_status import TransactionStatus
from app.utils.emails import (
    send_email_when_funding_reaches,
    send_email_when_transaction_succeeds,
)

router = APIRouter(prefix="/refunds", tags=["transactions"])


@router.post(
    "/{project_id}",
    status_code=status.HTTP_201_CREATED,
    response_model=List[schema.RefundOut],
)
async def refund_transactions(
    background_tasks: BackgroundTasks,
    project_id: int,
    db: Session = Depends(get_db),
):

    project = (
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

    all_crowdfund_transactions: List[models.Transaction] = (
        db.query(models.Transaction)
        .filter(models.Transaction.project_id == project_id)
        .filter(models.Transaction.refund == None)
        .all()
    )

    for transaction in all_crowdfund_transactions:
        amount_owed = transaction.amount * (-1)
        currency = transaction.currency
        person_owed = transaction.user_id
        quantity = transaction.quantity

        refund = models.Refund(
            amount=amount_owed,
            currency=currency,
            quantity=quantity,
            transaction_id=transaction.id,
            user_id=person_owed,
            project_id=project_id,
            status=TransactionStatus.SUCCESS,
        )

        try:
            db.add(refund)
            # send_email_when_refund_success(background_tasks, project, user_id)
        except Exception as error:
            print(error)
            refund.status = TransactionStatus.PENDING

        db.commit()

    return "yay"
