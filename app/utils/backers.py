def get_total_credits_bought(transactions, project_backer):
    total_credits_bought = 0
    for transaction in transactions:
        if project_backer == transaction.backer:
            total_credits_bought += transaction.quantity
    return total_credits_bought
