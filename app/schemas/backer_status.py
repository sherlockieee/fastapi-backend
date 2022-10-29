from enum import Enum


class BackerStatus(Enum):
    SUCCESS = "SUCCESS"
    PENDING = "PENDING"
    CANCELLED = "CANCELLED"
    BANNED = "BANNED"
