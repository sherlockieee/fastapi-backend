from typing import List
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr, BaseModel
from jinja2 import Environment, select_autoescape, PackageLoader
import sys

from app import models
from app.config import settings


env = Environment(
    loader=PackageLoader("app", "deps/email/templates"),
    autoescape=select_autoescape(["html", "xml"]),
)


class EmailSchema(BaseModel):
    email: List[EmailStr]


class Email:
    def __init__(self, name: str, email: List[EmailStr]):
        self.name = name
        self.sender = "Admin @ X | Kickstarter for Climate"
        self.email = email

    async def send_mail(self, subject, template, **kwargs):
        # Define the config
        conf = ConnectionConfig(
            MAIL_USERNAME=settings.EMAIL_USERNAME,
            MAIL_PASSWORD=settings.EMAIL_PASSWORD,
            MAIL_FROM=settings.EMAIL_FROM,
            MAIL_PORT=settings.EMAIL_PORT,
            MAIL_SERVER=settings.EMAIL_HOST,
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True,
        )
        # Generate the HTML template base on the template name
        template = env.get_template(f"{template}.html")
        html = template.render(name=self.name, subject=subject, **kwargs)
        # Define the message options
        message = MessageSchema(
            subject=subject, recipients=self.email, body=html, subtype="html"
        )

        # Send the email
        fm = FastMail(conf)
        await fm.send_message(message)

    async def send_transaction_success(self):
        await self.send_mail("Your transaction is successful!", "transaction_success")

    async def send_transaction_success_for_owner(
        self, person_supporting, no_of_credits, amount
    ):
        await self.send_mail(
            f"{person_supporting} bought credits from your project",
            "transaction_success_owner",
            person_supporting=person_supporting,
            no_of_credits=no_of_credits,
            amount=amount,
        )
