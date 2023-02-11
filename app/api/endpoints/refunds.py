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


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[schema.RefundOut])
def get_refunds(db: Session = Depends(get_db)):
    all_refunds = db.query(models.Refund).all()
    return all_refunds


@router.post(
    "/{project_id}",
    status_code=status.HTTP_201_CREATED,
    response_model=List[schema.RefundOut],
)
async def refund_project(
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
        .all()
    )

    print(all_crowdfund_transactions)

    all_refund_ids = []

    for transaction in all_crowdfund_transactions:
        if (
            transaction.refund is not None
            and transaction.refund.status == TransactionStatus.SUCCESS
        ):
            print("Already refunded")
            continue
        elif (
            transaction.refund is not None
            and transaction.refund.status == TransactionStatus.PENDING
        ):
            transaction.refund.status = TransactionStatus.SUCCESS
            db.commit()

            print("Successfully update")
            all_refund_ids.append(transaction.refund.id)
            continue

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
            db.commit()
            db.refresh(refund)
            all_refund_ids.append(refund.id)
        except Exception as error:
            print(error)
            refund.status = TransactionStatus.PENDING

        db.commit()

    all_refunds = (
        db.query(models.Refund).filter(models.Refund.id.in_(all_refund_ids)).all()
    )
    return all_refunds
