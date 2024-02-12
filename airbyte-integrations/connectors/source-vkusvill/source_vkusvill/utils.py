from datetime import timedelta


def seconds_to_humantime(seconds: int) -> str:
    """Convert seconds to human time format"""
    return str(timedelta(seconds=seconds))
