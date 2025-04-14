#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#


from typing import Any, Mapping


def safe_stream_state(stream_state: Mapping[str, Any], cursor_field: str) -> Mapping[str, Any]:
    state = stream_state.get(cursor_field)
    if isinstance(state, str):
        try:
            # Convert to float first to ensure it's a valid number, then cast to int
            numeric_state = int(float(state))
            return {**stream_state, cursor_field: numeric_state}
        except ValueError:
            pass
    return stream_state
