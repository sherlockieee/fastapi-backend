from typing import List
from app.schemas.transaction import TransactionOut
from app.schemas.transaction_status import TransactionType


def get_total_credits_bought(transactions: List[TransactionOut], project_backer):
    total_credits_bought = 0
    for transaction in transactions:
        if project_backer == transaction.user:
            total_credits_bought += transaction.quantity

    return total_credits_bought
