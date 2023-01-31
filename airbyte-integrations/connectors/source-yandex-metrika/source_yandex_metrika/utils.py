from datetime import datetime, timedelta
from typing import List

DATE_FORMAT = "%Y-%m-%d"


def daterange_days_list(date_from: str, date_to: str, days_delta: int = 1) -> List[str]:
    cursor_date = datetime.strptime(date_from, DATE_FORMAT)
    date_to = datetime.strptime(date_to, DATE_FORMAT)
    ranges = []
    while cursor_date <= date_to:
        if cursor_date + timedelta(days=days_delta) > date_to:
            ranges.append({"date_from": cursor_date.strftime(DATE_FORMAT), "date_to": date_to.strftime(DATE_FORMAT)})
            break
        ranges.append(
            {
                "date_from": cursor_date.strftime(DATE_FORMAT),
                "date_to": (cursor_date + timedelta(days=days_delta - 1)).strftime(DATE_FORMAT),
            }
        )
        cursor_date += timedelta(days=days_delta)
    return ranges


def yesterday_date() -> str:
    return datetime.strftime(datetime.now() - timedelta(1), DATE_FORMAT)


def today_minus_n_days_date(n_days: int) -> str:
    return datetime.strftime(datetime.now() - timedelta(n_days), DATE_FORMAT)
