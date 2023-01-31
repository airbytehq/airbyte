from datetime import datetime, timedelta


def get_yesterday_date() -> str:
    """Returns yesterday date (mm/dd/yyyy for requests report)."""
    return (datetime.now() - timedelta(1)).date().strftime("%Y/%m/%d") + "T23:59:59"


def get_today_minus_n_days_date(days: int):
    return (datetime.now() - timedelta(days)).date().strftime("%m/%d/%Y") + "T00:00:00"
