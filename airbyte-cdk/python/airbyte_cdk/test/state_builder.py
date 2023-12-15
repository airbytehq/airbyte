# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import Any, Dict, List


class StateBuilder:
    def __init__(self) -> None:
        self._state: List[Dict[str, Any]] = []

    def with_stream_state(self, stream_name: str, state: Any) -> "StateBuilder":
        self._state.append({
            "type": "STREAM",
            "stream": {
                "stream_state": state,
                "stream_descriptor": {
                    "name": stream_name
                }
            }
        })
        return self

    def build(self) -> List[Dict[str, Any]]:
        return self._state
