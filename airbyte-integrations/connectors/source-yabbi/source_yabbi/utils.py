from datetime import datetime, timedelta
from typing import Iterable, Tuple


def split_date_by_chunks(date_from: datetime, date_to: datetime, chunk_size_in_days: int) -> Iterable[Tuple[str, str]]:
    print("split_date_by_chunks,", date_from, date_to)
    cursor = date_from
    delta = timedelta(days=chunk_size_in_days)
    while cursor < date_to:
        if cursor + delta > date_to:
            yield (cursor, date_to)
            break
        yield (cursor, cursor + delta)
        cursor += delta + timedelta(days=1)
