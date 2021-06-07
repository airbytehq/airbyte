from datetime import date
from typing import Any,  Mapping
from dateutil.relativedelta import *


class Utils:

    @staticmethod
    def get_date_params(stream_slice: Mapping[str, Any], cursor_field: str):
        start_date = date.fromisoformat(
            stream_slice.get(cursor_field)) + relativedelta(days=1)
        end_date = date.fromisoformat(
            stream_slice.get(cursor_field)) + relativedelta(months=1)

        return start_date.isoformat(), end_date.isoformat()
