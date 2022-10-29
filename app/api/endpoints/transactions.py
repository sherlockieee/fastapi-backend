from typing import List
from fastapi import APIRouter, Depends, status, HTTPException, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session, joinedload


import app.models as models
from app.api.deps import get_current_active_user, get_db
from app.models.backers_projects_orders import BackerProjectOrder
from app.deps.email.email import Email
import app.schemas.transaction as schema
from app.schemas.backer_status import BackerStatus

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("/", status_code=200, response_model=List[schema.TransactionOut])
def get_transactions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    transactions = (
        db.query(BackerProjectOrder)
        .options(joinedload(BackerProjectOrder.backer))
        .options(joinedload(BackerProjectOrder.project))
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
            joinedload(models.Project.backers).options(
                joinedload(models.BackerProjectOrder.backer)
            )
        )
        .filter(models.Project.id == transaction.project_id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if (project.total_credits - project.credits_sold) < transaction_dict["quantity"]:
        raise HTTPException(
            status_code=404, detail="Buying more credits than is available."
        )

    new_transaction = models.BackerProjectOrder(
        **transaction_dict, backer_id=current_user.id, status=BackerStatus.SUCCESS
    )
    db.add(new_transaction)
    project.credits_sold += transaction_dict["quantity"]
    project.total_raised += transaction_dict["amount"]

    def get_id(backer):
        return backer["backer_id"]

    all_backers = set(map(get_id, jsonable_encoder(project.backers)))

    if current_user.id not in all_backers:
        project.total_backers += 1

    try:
        # send success email to backer
        Email(
            current_user.preferred_name, [current_user.email]
        ).send_transaction_success(background_tasks=background_tasks)
        # send success email to project owner
        Email(
            project.owner.preferred_name, [project.owner.email]
        ).send_transaction_success_for_owner(
            background_tasks=background_tasks,
            person_supporting=current_user.preferred_name,
            no_of_credits=transaction_dict["quantity"],
            amount=transaction_dict["amount"],
        )
        db.commit()
    except Exception as error:
        print(error)
        new_transaction.status = BackerStatus.PENDING
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="There was an error sending email",
        )

    transaction = (
        db.query(BackerProjectOrder)
        .options(joinedload(BackerProjectOrder.backer))
        .options(joinedload(BackerProjectOrder.project))
        .where(BackerProjectOrder.id == new_transaction.id)
        .one()
    )

    return transaction
