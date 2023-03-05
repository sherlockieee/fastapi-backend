from typing import List, Union
from fastapi import APIRouter, Depends, status, HTTPException, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session, joinedload, contains_eager


import app.models as models
from app.api.deps import get_current_active_user, get_db
import app.schemas.refund as schema
from app.schemas.transaction_status import TransactionStatus
from app.schemas.project_status import ProjectStatus


router = APIRouter(prefix="/refunds", tags=["transactions"])


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[schema.RefundOut])
def get_refunds(db: Session = Depends(get_db)):
    all_refunds = db.query(models.Refund).all()
    return all_refunds


@router.get("/project/{project_id}", response_model=List[schema.RefundOut])
def get_refunds_for_one_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    refunds = (
        db.query(models.Refund)
        .join(models.Refund.project)
        .join(models.Refund.user)
        .options(contains_eager(models.Refund.user))
        .options(contains_eager(models.Refund.project))
        .filter(models.Project.id == project_id)
        .filter(models.User.id == current_user.id)
        .all()
    )

    return refunds


@router.get(
    "/transaction/{transaction_id}", response_model=Union[schema.RefundOut, None]
)
def get_refund_for_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    refund = (
        db.query(models.Refund)
        .filter(models.Refund.transaction_id == transaction_id)
        .first()
    )

    if not refund:
        return

    if refund.user.id != current_user.id:
        raise HTTPException(status_code=401, detail="Not authorized")

    return refund


@router.post(
    "project/{project_id}",
    status_code=status.HTTP_201_CREATED,
    response_model=List[schema.RefundOut],
)
def refund_project(
    # background_tasks: BackgroundTasks,
    project_id: int,
    db: Session = Depends(get_db),
):
    print("refunding")

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

    elif project.status != ProjectStatus.FAIL:
        raise HTTPException(
            status_code=404,
            detail="Project doesn't have fail status so refund cannot happen",
        )

    all_crowdfund_transactions: List[models.Transaction] = (
        db.query(models.Transaction)
        .filter(models.Transaction.project_id == project_id)
        .all()
    )
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
            print("refund successfully")
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
