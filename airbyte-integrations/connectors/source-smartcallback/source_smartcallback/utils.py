from datetime import datetime, timedelta, date as datetime_date
import time


def get_last_month_timestamp() -> str:
    return str(int((datetime.now() - timedelta(31)).timestamp()))


def get_yesterday_timestamp() -> str:
    return str(int((datetime.now() - timedelta(0)).timestamp()))


def get_today_minus_n_days_timestamp(days: int) -> str:
    return str(int((datetime.now() - timedelta(days)).timestamp()))


def date_to_timestamp(date: str) -> str:
    return datetime_date.fromisoformat(date).strftime("%s")
