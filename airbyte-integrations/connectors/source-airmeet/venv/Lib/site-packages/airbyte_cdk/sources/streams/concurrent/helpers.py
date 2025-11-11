# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import List, Optional, Union

from airbyte_cdk.sources.streams import Stream


def get_primary_key_from_stream(
    stream_primary_key: Optional[Union[str, List[str], List[List[str]]]],
) -> List[str]:
    if stream_primary_key is None:
        return []
    elif isinstance(stream_primary_key, str):
        return [stream_primary_key]
    elif isinstance(stream_primary_key, list):
        are_all_elements_str = all(isinstance(k, str) for k in stream_primary_key)
        are_all_elements_list_of_size_one = all(
            isinstance(k, list) and len(k) == 1 for k in stream_primary_key
        )

        if are_all_elements_str:
            return stream_primary_key  # type: ignore # We verified all items in the list are strings
        elif are_all_elements_list_of_size_one:
            return list(map(lambda x: x[0], stream_primary_key))
        else:
            raise ValueError(f"Nested primary keys are not supported. Found {stream_primary_key}")
    else:
        raise ValueError(f"Invalid type for primary key: {stream_primary_key}")


def get_cursor_field_from_stream(stream: Stream) -> Optional[str]:
    if isinstance(stream.cursor_field, list):
        if len(stream.cursor_field) > 1:
            raise ValueError(
                f"Nested cursor fields are not supported. Got {stream.cursor_field} for {stream.name}"
            )
        elif len(stream.cursor_field) == 0:
            return None
        else:
            return stream.cursor_field[0]
    else:
        return stream.cursor_field
