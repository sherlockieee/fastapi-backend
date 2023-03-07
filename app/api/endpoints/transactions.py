from typing import List
from fastapi import (
    APIRouter,
    Depends,
    status,
    HTTPException,
    BackgroundTasks,
    Request,
    Header,
    Response,
)

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session, contains_eager, joinedload
import stripe


import app.models as models
from app.api.deps import get_current_active_user, get_db
from app.models.transactions import Transaction
import app.schemas.transaction as schema
import app.schemas.stripe as stripeSchema
from app.schemas.transaction_status import TransactionStatus, TransactionType
from app.schemas.project_status import ProjectStatus
from app.utils.emails import (
    send_email_when_funding_reaches,
    send_email_when_transaction_succeeds,
)
from app.config import settings

stripe.api_key = settings.STRIPE_API_KEY
endpoint_secret = settings.STRIPE_WEBHOOK_ENDPOINT_SECRET


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
    "/create-checkout-session",
    status_code=status.HTTP_200_OK,
)
def create_checkout_session(
    checkout: stripeSchema.PaymentIn,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    checkout_dict = jsonable_encoder(checkout)

    project = (
        db.query(models.Project)
        .options(
            joinedload(models.Project.users).options(
                joinedload(models.Transaction.user)
            )
        )
        .filter(models.Project.id == checkout.project_id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.status != ProjectStatus.IN_FUNDING:
        raise HTTPException(status_code=404, detail="Project is no longer in funding")

    if (project.total_credits - project.credits_sold) < checkout_dict["quantity"]:
        raise HTTPException(
            status_code=404, detail="Buying more credits than is available."
        )

    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    "price_data": {
                        "currency": checkout_dict["currency"].lower(),
                        "unit_amount": int(checkout_dict["amount"] * 100),
                        "product_data": {
                            "name": project.title,
                            "description": project.description,
                        },
                    },
                    "quantity": checkout_dict["quantity"],
                }
            ],
            metadata={
                "project_id": checkout_dict["project_id"],
                "quantity": checkout_dict["quantity"],
                "user_id": current_user.id,
            },
            client_reference_id=current_user.id,
            customer_email=current_user.email,
            mode="payment",
            payment_method_types=["card"],
            success_url=checkout_dict["successUrl"],
            cancel_url=checkout_dict["cancelUrl"],
        )

        return checkout_session.url
    except Exception as e:
        print(e)


@router.post("/webhook", status_code=status.HTTP_200_OK)
async def webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    stripe_signature: str = Header(None),
    db: Session = Depends(get_db),
):
    payload = await request.body()
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header=stripe_signature, secret=endpoint_secret
        )

    except ValueError as e:
        # Invalid payload
        print(e)
        return HTTPException(status_code=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        print(e)
        return HTTPException(status_code=400, detail="Invalid signature")

    # Handle the checkout.session.completed event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        # Save an order in your database, marked as 'awaiting payment'
        create_order(session)

        # Check if the order is already paid (for example, from a card payment)
        #
        # A delayed notification payment will have an `unpaid` status, as
        # you're still waiting for funds to be transferred from the customer's
        # account.
        if session.payment_status == "paid":
            # Fulfill the purchase
            fulfill_order(session, background_tasks, db)

    elif event["type"] == "checkout.session.async_payment_succeeded":
        session = event["data"]["object"]

        # Fulfill the purchase
        fulfill_order(session, background_tasks, db)

    elif event["type"] == "checkout.session.async_payment_failed":
        session = event["data"]["object"]

        # Send an email to the customer asking them to retry their order
    return Response(status_code=200)


def create_order(session):
    pass


def fulfill_order(session, background_tasks: BackgroundTasks, db):
    user_id = int(session["metadata"]["user_id"])
    project_id = int(session["metadata"]["project_id"])
    quantity = int(session["metadata"]["quantity"])
    amount = int(session["amount_total"]) / 100
    currency = session["currency"].upper()
    stripe_id = session["id"]

    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    current_user = db.query(models.User).filter(models.User.id == user_id).first()

    new_transaction = models.Transaction(
        project_id=project_id,
        quantity=quantity,
        amount=amount,
        currency=currency,
        user_id=user_id,
        stripe_id=stripe_id,
        status=TransactionStatus.SUCCESS,
    )
    db.add(new_transaction)
    project.credits_sold += quantity
    project.total_raised += amount
    db.commit()

    try:
        send_email_when_transaction_succeeds(
            background_tasks,
            {"quantity": quantity, "amount": amount},
            project.owner,
            current_user,
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
