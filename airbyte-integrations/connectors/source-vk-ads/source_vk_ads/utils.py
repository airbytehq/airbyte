import time
from datetime import datetime, timedelta

DATE_FORMAT = "%Y-%m-%d"


def xor(str1, str2):
    return bool(str1) ^ bool(str2)


def date_to_timestamp(date_str):
    return int(time.mktime(datetime.strptime(date_str, DATE_FORMAT).timetuple()))


def get_today_minus_n_days_date(last_days):
    return (datetime.now() - timedelta(last_days)).date().strftime(DATE_FORMAT)


def get_yesterday_date():
    return (datetime.now() - timedelta(1)).date().strftime(DATE_FORMAT)


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]