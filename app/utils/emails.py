from fastapi import BackgroundTasks

from app.deps.email.email import Email
from app.utils.backers import get_total_credits_bought


def send_email_when_transaction_succeeds(
    background_tasks: BackgroundTasks, transaction_dict, owner, backer
):
    # send success email to backer
    Email(backer.preferred_name, [backer.email]).send_transaction_success(
        background_tasks=background_tasks
    )
    # send success email to project owner
    Email(owner.preferred_name, [owner.email]).send_transaction_success_for_owner(
        background_tasks=background_tasks,
        person_supporting=backer.preferred_name,
        no_of_credits=transaction_dict["quantity"],
        amount=transaction_dict["amount"],
    )


def send_email_when_funding_reaches(background_tasks: BackgroundTasks, project):
    project_backers = set(transaction.backer for transaction in project.backers)

    for project_backer in project_backers:
        credits_bought = get_total_credits_bought(project.backers, project_backer)

        Email(
            project_backer.preferred_name, [project_backer.email]
        ).send_project_successfully_funded(
            background_tasks, project.title, credits_bought, project.credits_sold
        )

    # send success email to project owner
    Email(
        project.owner.preferred_name, [project.owner.email]
    ).send_project_successfully_funded_for_owner(
        background_tasks=background_tasks,
        project_name=project.title,
        no_of_backers=len(project_backers),
    )


def send_email_when_project_fails(background_tasks: BackgroundTasks, project):
    project_backers = set(transaction.backer for transaction in project.backers)

    for project_backer in project_backers:
        credits_bought = get_total_credits_bought(project.backers, project_backer)

        Email(project_backer.preferred_name, [project_backer.email]).send_project_fails(
            background_tasks, project.title, credits_bought, project.credits_sold
        )

    Email(project.owner.preferred_name, [project.owner.email]).send_project_fails_owner(
        background_tasks=background_tasks,
        project_name=project.title,
        no_of_backers=len(project_backers),
    )
