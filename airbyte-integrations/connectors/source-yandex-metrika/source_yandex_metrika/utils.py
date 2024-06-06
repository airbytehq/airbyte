import random
import string
from datetime import datetime, timedelta

DATE_FORMAT = "%Y-%m-%d"


def daterange_days_list(date_from: datetime, date_to: datetime, days_delta: int = 1) -> list[str]:
    cursor_date = date_from
    date_to = date_to

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


def yesterday_date() -> str:
    return datetime.strftime(datetime.now() - timedelta(1), DATE_FORMAT)


def today_minus_n_days_date(n_days: int) -> str:
    return datetime.strftime(datetime.now() - timedelta(n_days), DATE_FORMAT)


def random_output_filename() -> str:
    return f"output/{random_str(20)}.csv"


def random_str(n: int) -> str:
    return "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(n))


def partition_list(lst, n):
    # Calculate the length of each partition
    partition_size = len(lst) // n

    # Calculate the number of remaining elements after partitioning
    remaining = len(lst) % n

    # Build a list of partitions
    partitions = []
    start = 0
    for i in range(n):
        # Determine the end index of the partition, accounting for remaining elements
        end = start + partition_size
        if i < remaining:
            end += 1

        # Add the partition to the list
        partitions.append(lst[start:end])
        start = end

    return partitions
