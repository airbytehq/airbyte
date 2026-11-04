# Copyright (c) 2026 Albert Wong
# SPDX-License-Identifier: MIT
import json
import time
from contextlib import closing
from importlib.resources import files

from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    ConnectorSpecification,
    Status,
    SyncMode,
    Type,
)
from airbyte_cdk.sources import Source

from .backend import AdbcBackend, ConnectorError, validate_config
from .conversion import ConversionError


class SourceRedisAdbc(Source):
    def __init__(self, backend_factory=AdbcBackend):
        self.backend_factory = backend_factory

    def spec(self, logger):
        return ConnectorSpecification(**json.loads(files("source_redis_adbc").joinpath("spec.json").read_text()))

    def _backend(self, config):
        validate_config(config, self.spec(None).connectionSpecification)
        return self.backend_factory(config)

    def check(self, logger, config):
        try:
            self._backend(config).check()
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except (ConnectorError, ConversionError) as error:
            return AirbyteConnectionStatus(status=Status.FAILED, message=str(error))

    def discover(self, logger, config):
        return AirbyteCatalog(
            streams=[
                AirbyteStream(
                    name=table.name,
                    namespace=table.namespace,
                    json_schema=schema,
                    supported_sync_modes=[SyncMode.full_refresh],
                    source_defined_cursor=False,
                )
                for table, schema in self._backend(config).discover()
            ]
        )

    def read(self, logger, config, catalog, state=None):
        if state:
            raise ConnectorError("This full-refresh source does not accept incremental state.")
        selections = []
        for configured in catalog.streams:
            if configured.sync_mode != SyncMode.full_refresh:
                raise ConnectorError("Only full_refresh sync mode is supported.")
            selections.append((configured.stream.namespace, configured.stream.name, configured.stream.json_schema.get("properties", {})))
        with closing(self._backend(config).read(selections)) as records:
            for table, record in records:
                yield AirbyteMessage(
                    type=Type.RECORD,
                    record=AirbyteRecordMessage(
                        stream=table.name,
                        namespace=table.namespace,
                        data=record,
                        emitted_at=time.time_ns() // 1_000_000,
                    ),
                )
