from enum import Enum


class ProjectStatus(Enum):
    CREATED = "CREATED"  # Project gets created, not yet in funding
    IN_FUNDING = "IN_FUNDING"  # Project in funding stage
    SUCCESS = "SUCCESS"  # Project got all funding
    FAIL = "FAIL"  # Project did not get all funding
    BANNED = "BANNED"  # Project gets banned by admin
    IN_PROGRESS = "IN_PROGRESS"  # Project got funding and is currently being built
    CREDITS_AVAILABLE = "CREDITS_AVAILABLE"  # Projects built, carbon credits are available for retrieval
