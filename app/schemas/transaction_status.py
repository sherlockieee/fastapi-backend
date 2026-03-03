from enum import Enum


class TransactionStatus(Enum):
    SUCCESS = "SUCCESS"
    PENDING = "PENDING"
    CANCELLED = "CANCELLED"
    BANNED = "BANNED"


class TransactionType(Enum):
    CROWDFUND = "CROWDFUND"  # when a backer supports the project
    REFUND = "REFUND"  # when project doesn't work out, refund to backer
    PAYOUT = "PAYOUT"  # when project reaches its funding, payout to owner
