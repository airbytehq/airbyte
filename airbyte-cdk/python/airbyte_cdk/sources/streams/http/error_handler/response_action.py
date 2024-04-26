from enum import Enum

class ResponseAction(Enum):

    SUCCESS = "SUCCESS"
    RETRY = "RETRY"
    FAIL = "FAIL"
    IGNORE = "IGNORE"
