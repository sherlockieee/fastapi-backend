from typing import List
from fastapi import APIRouter, Depends, status, HTTPException, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session, contains_eager, joinedload


import app.models as models
from app.api.deps import get_current_active_user, get_db
from app.models.backers_projects_orders import BackerProjectOrder
import app.schemas.transaction as schema
from app.schemas.backer_status import BackerStatus
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
        db.query(BackerProjectOrder)
        .options(joinedload(BackerProjectOrder.backer))
        .options(joinedload(BackerProjectOrder.project))
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
        db.query(BackerProjectOrder)
        .join(BackerProjectOrder.project)
        .join(BackerProjectOrder.backer)
        .options(contains_eager(BackerProjectOrder.backer))
        .options(contains_eager(BackerProjectOrder.project))
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
            joinedload(models.Project.backers).options(
                joinedload(models.BackerProjectOrder.backer)
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
        send_email_when_transaction_succeeds(
            background_tasks, transaction_dict, project.owner, current_user
        )
    except Exception as error:
        print(error)
        new_transaction.status = BackerStatus.PENDING

    if project.total_raised >= project.funding_needed:
        project.status = ProjectStatus.SUCCESS
        try:
            send_email_when_funding_reaches(background_tasks, project)
        except Exception as error:
            print(error)

    db.commit()

    transaction = (
        db.query(BackerProjectOrder)
        .options(joinedload(BackerProjectOrder.backer))
        .options(joinedload(BackerProjectOrder.project))
        .where(BackerProjectOrder.id == new_transaction.id)
        .one()
    )

    return transaction
