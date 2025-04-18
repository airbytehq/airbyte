#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#


from typing import Any, Mapping


def safe_stream_state(stream_state: Mapping[str, Any], cursor_field: str) -> Mapping[str, Any]:
    result_state = {**stream_state}

    if cursor_field not in result_state and "state" in stream_state:
        result_state = stream_state["state"]

    raw_value = result_state.get(cursor_field)

    if isinstance(raw_value, str):
        try:
            # Convert to float first to ensure it's a valid number, then cast to int
            result_state[cursor_field] = int(float(raw_value))
        except ValueError:
            pass  # Leave the original string value if conversion fails

    return result_state
