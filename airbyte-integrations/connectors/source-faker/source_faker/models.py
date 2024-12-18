# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from __future__ import annotations

from types import MethodType

import orjson

from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    Type,
)
from airbyte_cdk.models.airbyte_protocol_serializers import (
    AirbyteMessageSerializer,
    ConfiguredAirbyteStreamSerializer,
)


def msg_to_json(self: AirbyteMessage) -> str:
    return orjson.dumps(self.to_dict()).decode("utf-8")


ConfiguredAirbyteStream.from_dict = ConfiguredAirbyteStreamSerializer.load
AirbyteMessage.to_dict = MethodType(AirbyteMessageSerializer.dump, AirbyteMessage)
AirbyteMessage.to_json = MethodType(msg_to_json, AirbyteMessage)


class AirbyteMessageWithCachedJSON(AirbyteMessage):
    """
    I a monkeypatch to AirbyteMessage which pre-renders the JSON-representation of the object upon initialization.
    This allows the JSON to be calculated in the process that builds the object rather than the main process.

    Note: We can't use @cache here because the LRU cache is not serializable when passed to child workers.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._json = self.to_json()
        self.json = self.from_json

    def to_json(self) -> dict:
        # return cached value (optimized for multiple calls with the same massage)
        return self._json


__all__ = [
    "AirbyteMessage",
    "AirbyteRecordMessage",
    "AirbyteMessageWithCachedJSON",
    "ConfiguredAirbyteCatalog",
    "ConfiguredAirbyteStream",
    "Type",
]
