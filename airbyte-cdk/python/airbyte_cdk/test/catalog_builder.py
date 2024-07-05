# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import Any, Dict, List, Union, overload

from airbyte_protocol.models import ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, SyncMode


class ConfiguredAirbyteStreamBuilder:
    def __init__(self) -> None:
        self._stream: Dict[str, Any] = {
            "stream": {
                "name": "any name",
                "json_schema": {},
                "supported_sync_modes": ["full_refresh", "incremental"],
                "source_defined_primary_key": [["id"]],
            },
            "primary_key": [["id"]],
            "sync_mode": "full_refresh",
            "destination_sync_mode": "overwrite",
        }

    def with_name(self, name: str) -> "ConfiguredAirbyteStreamBuilder":
        self._stream["stream"]["name"] = name  # type: ignore  # we assume that self._stream["stream"] is a Dict[str, Any]
        return self

    def with_sync_mode(self, sync_mode: SyncMode) -> "ConfiguredAirbyteStreamBuilder":
        self._stream["sync_mode"] = sync_mode.name
        return self

    def with_primary_key(self, pk: List[List[str]]) -> "ConfiguredAirbyteStreamBuilder":
        self._stream["primary_key"] = pk
        self._stream["stream"]["source_defined_primary_key"] = pk  # type: ignore  # we assume that self._stream["stream"] is a Dict[str, Any]
        return self

    def with_json_schema(self, json_schema: Dict[str, Any]) -> "ConfiguredAirbyteStreamBuilder":
        self._stream["stream"]["json_schema"] = json_schema
        return self

    def build(self) -> ConfiguredAirbyteStream:
        return ConfiguredAirbyteStream.parse_obj(self._stream)


class CatalogBuilder:
    def __init__(self) -> None:
        self._streams: List[ConfiguredAirbyteStreamBuilder] = []

    @overload
    def with_stream(self, name: ConfiguredAirbyteStreamBuilder) -> "CatalogBuilder":
        ...

    @overload
    def with_stream(self, name: str, sync_mode: SyncMode) -> "CatalogBuilder":
        ...

    def with_stream(self, name: Union[str, ConfiguredAirbyteStreamBuilder], sync_mode: Union[SyncMode, None] = None) -> "CatalogBuilder":
        # As we are introducing a fully fledge ConfiguredAirbyteStreamBuilder, we would like to deprecate the previous interface
        # with_stream(str, SyncMode)

        # to avoid a breaking change, `name` needs to stay in the API but this can be either a name or a builder
        name_or_builder = name
        builder = (
            name_or_builder
            if isinstance(name_or_builder, ConfiguredAirbyteStreamBuilder)
            else ConfiguredAirbyteStreamBuilder().with_name(name_or_builder).with_sync_mode(sync_mode)
        )
        self._streams.append(builder)
        return self

    def build(self) -> ConfiguredAirbyteCatalog:
        return ConfiguredAirbyteCatalog(streams=list(map(lambda builder: builder.build(), self._streams)))
