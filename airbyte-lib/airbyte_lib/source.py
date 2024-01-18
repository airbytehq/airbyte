# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from __future__ import annotations

import json
import tempfile
from contextlib import contextmanager, suppress
from typing import TYPE_CHECKING, Any

import jsonschema

from airbyte_protocol.models import (
    AirbyteCatalog,
    AirbyteMessage,
    AirbyteRecordMessage,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    ConnectorSpecification,
    DestinationSyncMode,
    Status,
    SyncMode,
    Type,
)

from airbyte_lib._factories.cache_factories import get_default_cache
from airbyte_lib._util import protocol_util  # Internal utility functions
from airbyte_lib.results import ReadResult
from airbyte_lib.telemetry import (
    CacheTelemetryInfo,
    SyncState,
    send_telemetry,
    streaming_cache_info,
)


if TYPE_CHECKING:
    from collections.abc import Generator, Iterable, Iterator

    from airbyte_lib._executor import Executor
    from airbyte_lib.caches import SQLCacheBase


@contextmanager
def as_temp_files(files: list[Any]) -> Generator[list[Any], Any, None]:
    temp_files: list[Any] = []
    try:
        for content in files:
            temp_file = tempfile.NamedTemporaryFile(mode="w+t", delete=True)
            temp_file.write(
                json.dumps(content) if isinstance(content, dict) else content,
            )
            temp_file.flush()
            temp_files.append(temp_file)
        yield [file.name for file in temp_files]
    finally:
        for temp_file in temp_files:
            with suppress(Exception):
                temp_file.close()


class Source:
    """A class representing a source that can be called."""

    def __init__(
        self,
        executor: Executor,
        name: str,
        config: dict[str, Any] | None = None,
        streams: list[str] | None = None,
    ) -> None:
        self._processed_records = 0
        self.executor = executor
        self.name = name
        self.streams: list[str] | None = None
        self._processed_records = 0
        self._config_dict: dict[str, Any] | None = None
        self._last_log_messages: list[str] = []
        self._discovered_catalog: AirbyteCatalog | None = None
        self._spec: ConnectorSpecification | None = None
        if config is not None:
            self.set_config(config)
        if streams is not None:
            self.set_streams(streams)

    def set_streams(self, streams: list[str]) -> None:
        available_streams = self.get_available_streams()
        for stream in streams:
            if stream not in available_streams:
                raise Exception(
                    f"Stream {stream} is not available for connector {self.name}. "
                    f"Choose from: {available_streams}",
                )
        self.streams = streams

    def set_config(self, config: dict[str, Any]) -> None:
        self._validate_config(config)
        self._config_dict = config

    @property
    def _config(self) -> dict[str, Any]:
        if self._config_dict is None:
            raise Exception(
                "Config is not set, either set in get_connector or via source.set_config",
            )
        return self._config_dict

    def _discover(self) -> AirbyteCatalog:
        """Call discover on the connector.

        This involves the following steps:
        * Write the config to a temporary file
        * execute the connector with discover --config <config_file>
        * Listen to the messages and return the first AirbyteCatalog that comes along.
        * Make sure the subprocess is killed when the function returns.
        """
        with as_temp_files([self._config]) as [config_file]:
            for msg in self._execute(["discover", "--config", config_file]):
                if msg.type == Type.CATALOG and msg.catalog:
                    return msg.catalog
            raise Exception(
                f"Connector did not return a catalog. Last logs: {self._last_log_messages}",
            )

    def _validate_config(self, config: dict[str, Any]) -> None:
        """Validate the config against the spec."""
        spec = self._get_spec(force_refresh=False)
        jsonschema.validate(config, spec.connectionSpecification)

    def get_available_streams(self) -> list[str]:
        """Get the available streams from the spec."""
        return [s.name for s in self._discover().streams]

    def _get_spec(self, *, force_refresh: bool = False) -> ConnectorSpecification:
        """Call spec on the connector.

        This involves the following steps:
        * execute the connector with spec
        * Listen to the messages and return the first AirbyteCatalog that comes along.
        * Make sure the subprocess is killed when the function returns.
        """
        if force_refresh or self._spec is None:
            for msg in self._execute(["spec"]):
                if msg.type == Type.SPEC and msg.spec:
                    self._spec = msg.spec
                    break

        if self._spec:
            return self._spec

        raise Exception(
            f"Connector did not return a spec. Last logs: {self._last_log_messages}",
        )

    @property
    def raw_catalog(self) -> AirbyteCatalog:
        """Get the raw catalog for the given streams."""
        return self._discover()

    @property
    def configured_catalog(self) -> ConfiguredAirbyteCatalog:
        """Get the configured catalog for the given streams."""
        if self._discovered_catalog is None:
            self._discovered_catalog = self._discover()

        return ConfiguredAirbyteCatalog(
            streams=[
                ConfiguredAirbyteStream(
                    stream=s,
                    sync_mode=SyncMode.full_refresh,
                    destination_sync_mode=DestinationSyncMode.overwrite,
                    primary_key=None,
                )
                for s in self._discovered_catalog.streams
                if self.streams is None or s.name in self.streams
            ],
        )

    def get_records(self, stream: str) -> Iterator[dict[str, Any]]:
        """Read a stream from the connector.

        This involves the following steps:
        * Call discover to get the catalog
        * Generate a configured catalog that syncs the given stream in full_refresh mode
        * Write the configured catalog and the config to a temporary file
        * execute the connector with read --config <config_file> --catalog <catalog_file>
        * Listen to the messages and return the first AirbyteRecordMessages that come along.
        * Make sure the subprocess is killed when the function returns.
        """
        catalog = self._discover()
        configured_catalog = ConfiguredAirbyteCatalog(
            streams=[
                ConfiguredAirbyteStream(
                    stream=s,
                    sync_mode=SyncMode.full_refresh,
                    destination_sync_mode=DestinationSyncMode.overwrite,
                )
                for s in catalog.streams
                if s.name == stream
            ],
        )
        if len(configured_catalog.streams) == 0:
            raise ValueError(
                f"Stream {stream} is not available for connector {self.name}, "
                f"choose from {self.get_available_streams()}",
            )

        iterator: Iterable[dict[str, Any]] = protocol_util.airbyte_messages_to_record_dicts(
            self._read_with_catalog(streaming_cache_info, configured_catalog),
        )
        yield from iterator  # TODO: Refactor to use LazyDataset here

    def check(self) -> None:
        """Call check on the connector.

        This involves the following steps:
        * Write the config to a temporary file
        * execute the connector with check --config <config_file>
        * Listen to the messages and return the first AirbyteCatalog that comes along.
        * Make sure the subprocess is killed when the function returns.
        """
        with as_temp_files([self._config]) as [config_file]:
            for msg in self._execute(["check", "--config", config_file]):
                if msg.type == Type.CONNECTION_STATUS and msg.connectionStatus:
                    if msg.connectionStatus.status != Status.FAILED:
                        return  # Success!

                    raise Exception(
                        f"Connector returned failed status: {msg.connectionStatus.message}",
                    )
            raise Exception(
                f"Connector did not return check status. Last logs: {self._last_log_messages}",
            )

    def install(self) -> None:
        """Install the connector if it is not yet installed."""
        self.executor.install()

    def uninstall(self) -> None:
        """Uninstall the connector if it is installed.

        This only works if the use_local_install flag wasn't used and installation is managed by
        airbyte-lib.
        """
        self.executor.uninstall()

    def _read(self, cache_info: CacheTelemetryInfo) -> Iterable[AirbyteRecordMessage]:
        """
        Call read on the connector.

        This involves the following steps:
        * Call discover to get the catalog
        * Generate a configured catalog that syncs all streams in full_refresh mode
        * Write the configured catalog and the config to a temporary file
        * execute the connector with read --config <config_file> --catalog <catalog_file>
        * Listen to the messages and return the AirbyteRecordMessages that come along.
        """
        catalog = self._discover()
        configured_catalog = ConfiguredAirbyteCatalog(
            streams=[
                ConfiguredAirbyteStream(
                    stream=s,
                    sync_mode=SyncMode.full_refresh,
                    destination_sync_mode=DestinationSyncMode.overwrite,
                )
                for s in catalog.streams
                if self.streams is None or s.name in self.streams
            ],
        )
        yield from self._read_with_catalog(cache_info, configured_catalog)

    def _read_with_catalog(
        self,
        cache_info: CacheTelemetryInfo,
        catalog: ConfiguredAirbyteCatalog,
    ) -> Iterator[AirbyteMessage]:
        """Call read on the connector.

        This involves the following steps:
        * Write the config to a temporary file
        * execute the connector with read --config <config_file> --catalog <catalog_file>
        * Listen to the messages and return the AirbyteRecordMessages that come along.
        * Send out telemetry on the performed sync (with information about which source was used and
          the type of the cache)
        """
        source_tracking_information = self.executor.get_telemetry_info()
        send_telemetry(source_tracking_information, cache_info, SyncState.STARTED)
        try:
            with as_temp_files([self._config, catalog.json()]) as [
                config_file,
                catalog_file,
            ]:
                yield from self._execute(
                    ["read", "--config", config_file, "--catalog", catalog_file],
                )
        except Exception:
            send_telemetry(
                source_tracking_information, cache_info, SyncState.FAILED, self._processed_records
            )
            raise
        finally:
            send_telemetry(
                source_tracking_information,
                cache_info,
                SyncState.SUCCEEDED,
                self._processed_records,
            )

    def _add_to_logs(self, message: str) -> None:
        self._last_log_messages.append(message)
        self._last_log_messages = self._last_log_messages[-10:]

    def _execute(self, args: list[str]) -> Iterator[AirbyteMessage]:
        """Execute the connector with the given arguments.

        This involves the following steps:
        * Locate the right venv. It is called ".venv-<connector_name>"
        * Spawn a subprocess with .venv-<connector_name>/bin/<connector-name> <args>
        * Read the output line by line of the subprocess and serialize them AirbyteMessage objects.
          Drop if not valid.
        """
        self.executor.ensure_installation()

        try:
            self._last_log_messages = []
            for line in self.executor.execute(args):
                try:
                    message = AirbyteMessage.parse_raw(line)
                    yield message
                    if message.type == Type.LOG:
                        self._add_to_logs(message.log.message)
                except Exception:
                    self._add_to_logs(line)
        except Exception as e:
            raise Exception(f"Execution failed. Last logs: {self._last_log_messages}") from e

    def _tally_records(
        self,
        messages: Iterable[AirbyteRecordMessage],
    ) -> Generator[AirbyteRecordMessage, Any, None]:
        """This method simply tallies the number of records processed and yields the messages."""
        self._processed_records = 0  # Reset the counter before we start
        for message in messages:
            self._processed_records += 1
            yield message

    def read(self, cache: SQLCacheBase | None = None) -> ReadResult:
        if cache is None:
            cache = get_default_cache()

        cache.register_source(source_name=self.name, source_catalog=self.configured_catalog)
        cache.process_airbyte_messages(self._tally_records(self._read(cache.get_telemetry_info())))

        return ReadResult(
            processed_records=self._processed_records,
            cache=cache,
        )
