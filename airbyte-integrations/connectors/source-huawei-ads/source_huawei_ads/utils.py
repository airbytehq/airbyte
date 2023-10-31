from datetime import datetime, timedelta
from typing import List


def daterange_days_list(date_from: datetime, date_to: datetime, days_delta: int = 1) -> List[str]:
    cursor_date = date_from
    ranges = []
    while cursor_date <= date_to:
        if cursor_date + timedelta(days=days_delta) > date_to:
            ranges.append({"date_from": cursor_date, "date_to": date_to})
            break
        ranges.append(
            {
                "date_from": cursor_date,
                "date_to": cursor_date + timedelta(days=days_delta - 1),
            }
        )
        cursor_date += timedelta(days=days_delta)
    return ranges
