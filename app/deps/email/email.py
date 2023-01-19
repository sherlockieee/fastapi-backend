from typing import List
from fastapi import BackgroundTasks
from starlette.responses import JSONResponse
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr, BaseModel
from jinja2 import Environment, select_autoescape, PackageLoader

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
        self.sender = "Admin @ CreX"
        self.email = email

    def generate_mail(self, subject: str, template: str, **kwargs):
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
        message = MessageSchema(
            subject=subject, recipients=self.email, body=html, subtype="html"
        )
        return conf, message

    async def send_mail_async(self, subject: str, template: str, **kwargs):
        conf, message = self.generate_mail(subject, template, **kwargs)
        fm = FastMail(conf)
        await fm.send_message(message)

        return JSONResponse(status_code=200, content={"message": "email has been sent"})

    def send_email_background(
        self, background_tasks: BackgroundTasks, subject: str, template: str, **kwargs
    ):

        conf, message = self.generate_mail(subject, template, **kwargs)
        fm = FastMail(conf)
        background_tasks.add_task(fm.send_message, message)

        return JSONResponse(status_code=200, content={"message": "email has been sent"})

    def send_transaction_success(self, background_tasks):
        self.send_email_background(
            background_tasks=background_tasks,
            subject="Your transaction is successful!",
            template="transaction_success",
        )

    def send_transaction_success_for_owner(
        self, background_tasks, person_supporting, no_of_credits, amount
    ):
        self.send_email_background(
            background_tasks=background_tasks,
            subject=f"{person_supporting} bought credits from your project",
            template="transaction_success_owner",
            person_supporting=person_supporting,
            no_of_credits=no_of_credits,
            amount=amount,
        )

    def send_project_successfully_funded(
        self, background_tasks, project_name, no_of_credits_bought, no_of_credits_sold
    ):
        self.send_email_background(
            background_tasks,
            f"The project you support, {project_name}, is fully funded!",
            "project_fully_funded",
            project_name=project_name,
            no_of_credits_bought=no_of_credits_bought,
            no_of_credits_sold=no_of_credits_sold,
        )

    def send_project_successfully_funded_for_owner(
        self,
        background_tasks,
        project_name,
        no_of_backers,
    ):
        self.send_email_background(
            background_tasks,
            f"Your project {project_name} is fully funded!",
            "project_fully_funded_owner",
            project_name=project_name,
            no_of_backers=no_of_backers,
        )

    def send_project_fails(self, background_tasks, no_of_credits_bought, project_name):
        self.send_email_background(
            background_tasks,
            f"Refunding from your crowdfunding project {project_name}",
            "project_fails",
            project_name=project_name,
            no_of_credits_bought=no_of_credits_bought,
        )

    def send_project_fails_owner(self, background_tasks, project_name):
        self.send_email_background(
            background_tasks,
            f"Your project {project_name} did not reach its crowdfunding goals",
            "project_fails_owner",
            project_name=project_name,
        )
