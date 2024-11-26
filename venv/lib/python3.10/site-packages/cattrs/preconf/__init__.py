from datetime import datetime


def validate_datetime(v, _):
    if not isinstance(v, datetime):
        raise Exception(f"Expected datetime, got {v}")
    return v
