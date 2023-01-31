from datetime import datetime


def dates_to_range(date_from: datetime, date_to: datetime):
    return datetime.strftime(date_from, "%Y-%m-%d") + "--" + datetime.strftime(date_to, "%Y-%m-%d")
