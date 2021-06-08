from typing import Any,  Mapping
import pendulum


class Utils:

    @staticmethod
    def get_date_params(stream_slice: Mapping[str, Any], cursor_field: str):
        start_date = pendulum.parse(
            stream_slice.get(cursor_field)).add(days=1)
        end_date = pendulum.parse(
            stream_slice.get(cursor_field)).add(months=1)

        return start_date.to_date_string(), end_date.to_date_string()
