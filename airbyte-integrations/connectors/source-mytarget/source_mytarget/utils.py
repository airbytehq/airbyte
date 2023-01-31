from datetime import datetime, timedelta

DATE_FORMAT = "%Y-%m-%d"


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def yesterday_minus_n_days(n_days: int):
    date = datetime.now() - timedelta(n_days)
    return date.strftime(DATE_FORMAT)


def date_minus_n_days(date: str, n_days: int):
    date = datetime.strptime(date, DATE_FORMAT) - timedelta(n_days)
    return date.strftime(DATE_FORMAT)
