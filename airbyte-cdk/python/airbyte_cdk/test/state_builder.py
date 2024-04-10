# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import Any, List

from airbyte_protocol.models import AirbyteStateMessage


class StateBuilder:
    def __init__(self) -> None:
        self._state: List[AirbyteStateMessage] = []

    def with_stream_state(self, stream_name: str, state: Any) -> "StateBuilder":
        self._state.append(AirbyteStateMessage.parse_obj({
            "type": "STREAM",
            "stream": {
                "stream_state": state,
                "stream_descriptor": {
                    "name": stream_name
                }
            }
        }))
        return self

    def build(self) -> List[AirbyteStateMessage]:
        return self._state
