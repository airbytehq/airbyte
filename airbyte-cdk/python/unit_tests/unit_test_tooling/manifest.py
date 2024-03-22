#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from copy import deepcopy


class ManifestStreamBuilder:
    _JSON_FILE_SCHEMA = {"type": "JsonFileSchemaLoader"}

    def __init__(self) -> None:
        self._schema = self._JSON_FILE_SCHEMA
        self._name = "a default stream name"
        self._definitions = {}

    def with_name(self, name: str) -> 'ManifestStreamBuilder':
        self._name = name
        return self

    def with_schema(self, inline: bool, by_ref: str = "") -> 'ManifestStreamBuilder':
        schema = {
                "type": "InlineSchemaLoader",
                "schema": {
                    "$schema": "http://json-schema.org/schema#",
                    "properties": {},
                    "type": "object"
                }
            } if inline else deepcopy(self._JSON_FILE_SCHEMA)

        if by_ref:
            self._definitions[by_ref] = schema
            self._schema = {"$ref": f"#/definitions/{by_ref}"}
        else:
            self._schema = schema
        return self

    def get_definitions(self):
        return self._definitions

    def build(self):
        return {
            "type": "DeclarativeStream",
            "name": self._name,
            "primary_key": [],
            "schema_loader": self._schema,
            "retriever": {
                "type": "SimpleRetriever",
                "requester": {
                    "type": "HttpRequester",
                    "url_base": "https://api.apilayer.com",
                    "path": "/exchangerates_data/latest",
                    "http_method": "GET",
                },
                "record_selector": {
                    "type": "RecordSelector",
                    "extractor": {
                        "type": "DpathExtractor",
                        "field_path": []
                    }
                },
            }
        }


class ManifestBuilder:
    def __init__(self) -> None:
        self._streams = []
        self._definitions = {}
        self._incremental_sync = None
        self._partition_router = None

    def with_list_partition_router(self, cursor_field, partitions) -> 'ManifestBuilder':
        self._partition_router = {
            "type": "ListPartitionRouter",
            "cursor_field": cursor_field,
            "values": partitions,
        }
        return self

    def with_incremental_sync(self, start_datetime, end_datetime, datetime_format, cursor_field, step, cursor_granularity) -> 'ManifestBuilder':
        self._incremental_sync = {
            "type": "DatetimeBasedCursor",
            "start_datetime": start_datetime,
            "end_datetime": end_datetime,
            "datetime_format": datetime_format,
            "cursor_field": cursor_field,
            "step": step,
            "cursor_granularity": cursor_granularity
        }
        return self

    def without_spec(self) -> 'ManifestBuilder':
        # Nothing to do as the default manifest in `build` doesn't have a spec
        return self

    def with_stream(self, stream: ManifestStreamBuilder, by_ref: str = "") -> 'ManifestBuilder':
        if self._definitions.keys() & stream.get_definitions().keys():
            raise ValueError(f"Duplicated definitions for {self._definitions.keys() & stream.get_definitions().keys()}")

        self._definitions = self._definitions | stream.get_definitions()
        if by_ref:
            self._streams.append(f"#/definitions/{by_ref}")
            self._definitions[by_ref] = stream.build()
        else:
            self._streams.append(stream.build())
        return self

    def build(self):
        manifest = {
            "version": "0.47.0",
            "type": "DeclarativeSource",
            "check": {
                "type": "CheckStream",
                "stream_names": [
                    "Rates"
                ]
            },
            "streams": self._streams if self._streams else [ManifestStreamBuilder().build()],
            "definitions": self._definitions
        }
        if self._incremental_sync:
            manifest["streams"][0]["incremental_sync"] = self._incremental_sync
        if self._partition_router:
            manifest["streams"][0]["retriever"]["partition_router"] = self._partition_router
        return manifest
