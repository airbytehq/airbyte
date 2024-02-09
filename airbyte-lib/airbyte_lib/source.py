# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from __future__ import annotations

import json
import tempfile
import warnings
from contextlib import contextmanager, suppress
from typing import TYPE_CHECKING, Any

import jsonschema
import pendulum
import yaml
from rich import print

from airbyte_protocol.models import (
    AirbyteCatalog,
    AirbyteMessage,
    AirbyteStateMessage,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    ConnectorSpecification,
    DestinationSyncMode,
    Status,
    SyncMode,
    TraceType,
    Type,
)

from airbyte_lib import exceptions as exc
from airbyte_lib._factories.cache_factories import get_default_cache
from airbyte_lib._util import protocol_util
from airbyte_lib._util.text_util import lower_case_set  # Internal utility functions
from airbyte_lib.datasets._lazy import LazyDataset
from airbyte_lib.progress import progress
from airbyte_lib.results import ReadResult
from airbyte_lib.strategies import WriteStrategy
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
def as_temp_files(files_contents: list[Any]) -> Generator[list[str], Any, None]:
    """Write the given contents to temporary files and yield the file paths as strings."""
    temp_files: list[Any] = []
    try:
        for content in files_contents:
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
        *,
        validate: bool = False,
    ) -> None:
        """Initialize the source.

        If config is provided, it will be validated against the spec if validate is True.
        """
        self.executor = executor
        self.name = name
        self._processed_records = 0
        self._config_dict: dict[str, Any] | None = None
        self._last_log_messages: list[str] = []
        self._discovered_catalog: AirbyteCatalog | None = None
        self._spec: ConnectorSpecification | None = None
        self._selected_stream_names: list[str] = []
        if config is not None:
            self.set_config(config, validate=validate)
        if streams is not None:
            self.set_streams(streams)

    def set_streams(self, streams: list[str]) -> None:
        """Deprecated. See select_streams()."""
        warnings.warn(
            "The 'set_streams' method is deprecated and will be removed in a future version. "
            "Please use the 'select_streams' method instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.select_streams(streams)

    def select_all_streams(self) -> None:
        """Select all streams.

        This is a more streamlined equivalent to:
        > source.select_streams(source.get_available_streams()).
        """
        self._selected_stream_names = self.get_available_streams()

    def select_streams(self, streams: list[str]) -> None:
        """Select the stream names that should be read from the connector.

        Currently, if this is not set, all streams will be read.
        """
        available_streams = self.get_available_streams()
        for stream in streams:
            if stream not in available_streams:
                raise exc.AirbyteStreamNotFoundError(
                    stream_name=stream,
                    connector_name=self.name,
                    available_streams=available_streams,
                )
        self._selected_stream_names = streams

    def get_selected_streams(self) -> list[str]:
        """Get the selected streams.

        If no streams are selected, return an empty list.
        """
        return self._selected_stream_names

    def set_config(
        self,
        config: dict[str, Any],
        *,
        validate: bool = False,
    ) -> None:
        """Set the config for the connector.

        If validate is True, raise an exception if the config fails validation.

        If validate is False, validation will be deferred until check() or validate_config()
        is called.
        """
        if validate:
            self.validate_config(config)

        self._config_dict = config

    def get_config(self) -> dict[str, Any]:
        """Get the config for the connector."""
        return self._config

    @property
    def _config(self) -> dict[str, Any]:
        if self._config_dict is None:
            raise exc.AirbyteConnectorConfigurationMissingError(
                guidance="Provide via get_source() or set_config()"
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
            raise exc.AirbyteConnectorMissingCatalogError(
                log_text=self._last_log_messages,
            )

    def validate_config(self, config: dict[str, Any] | None = None) -> None:
        """Validate the config against the spec.

        If config is not provided, the already-set config will be validated.
        """
        spec = self._get_spec(force_refresh=False)
        config = self._config if config is None else config
        jsonschema.validate(config, spec.connectionSpecification)

    def get_available_streams(self) -> list[str]:
        """Get the available streams from the spec."""
        return [s.name for s in self.discovered_catalog.streams]

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

        raise exc.AirbyteConnectorMissingSpecError(
            log_text=self._last_log_messages,
        )

    @property
    def _yaml_spec(self) -> str:
        """Get the spec as a yaml string.

        For now, the primary use case is for writing and debugging a valid config for a source.

        This is private for now because we probably want better polish before exposing this
        as a stable interface. This will also get easier when we have docs links with this info
        for each connector.
        """
        spec_obj: ConnectorSpecification = self._get_spec()
        spec_dict = spec_obj.dict(exclude_unset=True)
        # convert to a yaml string
        return yaml.dump(spec_dict)

    @property
    def docs_url(self) -> str:
        """Get the URL to the connector's documentation."""
        # TODO: Replace with docs URL from metadata when available
        return "https://docs.airbyte.com/integrations/sources/" + self.name.lower().replace(
            "source-", ""
        )

    @property
    def discovered_catalog(self) -> AirbyteCatalog:
        """Get the raw catalog for the given streams.

        If the catalog is not yet known, we call discover to get it.
        """
        if self._discovered_catalog is None:
            self._discovered_catalog = self._discover()

        return self._discovered_catalog

    @property
    def configured_catalog(self) -> ConfiguredAirbyteCatalog:
        """Get the configured catalog for the given streams.

        If the raw catalog is not yet known, we call discover to get it.

        If no specific streams are selected, we return a catalog that syncs all available streams.

        TODO: We should consider disabling by default the streams that the connector would
        disable by default. (For instance, streams that require a premium license are sometimes
        disabled by default within the connector.)
        """
        # Ensure discovered catalog is cached before we start
        _ = self.discovered_catalog

        # Filter for selected streams if set, otherwise use all available streams:
        streams_filter: list[str] = self._selected_stream_names or self.get_available_streams()

        return ConfiguredAirbyteCatalog(
            streams=[
                ConfiguredAirbyteStream(
                    stream=stream,
                    destination_sync_mode=DestinationSyncMode.overwrite,
                    primary_key=stream.source_defined_primary_key,
                    # TODO: The below assumes all sources can coalesce from incremental sync to
                    # full_table as needed. CDK supports this, so it might be safe:
                    sync_mode=SyncMode.incremental,
                )
                for stream in self.discovered_catalog.streams
                if stream.name in streams_filter
            ],
        )

    def get_records(self, stream: str) -> LazyDataset:
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
            raise exc.AirbyteLibInputError(
                message="Requested stream does not exist.",
                context={
                    "stream": stream,
                    "available_streams": self.get_available_streams(),
                    "connector_name": self.name,
                },
            ) from KeyError(stream)

        configured_stream = configured_catalog.streams[0]
        all_properties = set(configured_stream.stream.json_schema["properties"].keys())

        def _with_missing_columns(records: Iterable[dict[str, Any]]) -> Iterator[dict[str, Any]]:
            """Add missing columns to the record with null values."""
            for record in records:
                existing_properties_lower = lower_case_set(record.keys())
                appended_dict = {
                    prop: None
                    for prop in all_properties
                    if prop.lower() not in existing_properties_lower
                }
                yield {**record, **appended_dict}

        iterator: Iterator[dict[str, Any]] = _with_missing_columns(
            protocol_util.airbyte_messages_to_record_dicts(
                self._read_with_catalog(
                    streaming_cache_info,
                    configured_catalog,
                ),
            )
        )
        return LazyDataset(iterator)

    def check(self) -> None:
        """Call check on the connector.

        This involves the following steps:
        * Write the config to a temporary file
        * execute the connector with check --config <config_file>
        * Listen to the messages and return the first AirbyteCatalog that comes along.
        * Make sure the subprocess is killed when the function returns.
        """
        with as_temp_files([self._config]) as [config_file]:
            try:
                for msg in self._execute(["check", "--config", config_file]):
                    if msg.type == Type.CONNECTION_STATUS and msg.connectionStatus:
                        if msg.connectionStatus.status != Status.FAILED:
                            print(f"Connection check succeeded for `{self.name}`.")
                            return

                        raise exc.AirbyteConnectorCheckFailedError(
                            help_url=self.docs_url,
                            context={
                                "failure_reason": msg.connectionStatus.message,
                            },
                        )
                raise exc.AirbyteConnectorCheckFailedError(log_text=self._last_log_messages)
            except exc.AirbyteConnectorReadError as ex:
                raise exc.AirbyteConnectorCheckFailedError(
                    message="The connector failed to check the connection.",
                    log_text=ex.log_text,
                ) from ex

    def install(self) -> None:
        """Install the connector if it is not yet installed."""
        self.executor.install()
        print("For configuration instructions, see: \n" f"{self.docs_url}#reference\n")

    def uninstall(self) -> None:
        """Uninstall the connector if it is installed.

        This only works if the use_local_install flag wasn't used and installation is managed by
        airbyte-lib.
        """
        self.executor.uninstall()

    def _read(
        self,
        cache_info: CacheTelemetryInfo,
        state: list[AirbyteStateMessage] | None = None,
    ) -> Iterable[AirbyteMessage]:
        """
        Call read on the connector.

        This involves the following steps:
        * Call discover to get the catalog
        * Generate a configured catalog that syncs all streams in full_refresh mode
        * Write the configured catalog and the config to a temporary file
        * execute the connector with read --config <config_file> --catalog <catalog_file>
        * Listen to the messages and return the AirbyteMessage that come along.
        """
        # Ensure discovered and configured catalog properties are cached before we start reading
        _ = self.discovered_catalog
        _ = self.configured_catalog
        yield from self._read_with_catalog(
            cache_info,
            catalog=self.configured_catalog,
            state=state,
        )

    def _read_with_catalog(
        self,
        cache_info: CacheTelemetryInfo,
        catalog: ConfiguredAirbyteCatalog,
        state: list[AirbyteStateMessage] | None = None,
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
        sync_failed = False
        self._processed_records = 0  # Reset the counter before we start
        try:
            with as_temp_files(
                [self._config, catalog.json(), json.dumps(state) if state else "[]"]
            ) as [
                config_file,
                catalog_file,
                state_file,
            ]:
                yield from self._execute(
                    [
                        "read",
                        "--config",
                        config_file,
                        "--catalog",
                        catalog_file,
                        "--state",
                        state_file,
                    ],
                )
        except Exception:
            send_telemetry(
                source_tracking_information, cache_info, SyncState.FAILED, self._processed_records
            )
            sync_failed = True
            raise
        finally:
            if not sync_failed:
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
        # Fail early if the connector is not installed.
        self.executor.ensure_installation(auto_fix=False)

        try:
            self._last_log_messages = []
            for line in self.executor.execute(args):
                try:
                    message = AirbyteMessage.parse_raw(line)
                    if message.type is Type.RECORD:
                        self._processed_records += 1
                    if message.type == Type.LOG:
                        self._add_to_logs(message.log.message)
                    if message.type == Type.TRACE and message.trace.type == TraceType.ERROR:
                        self._add_to_logs(message.trace.error.message)
                    yield message
                except Exception:
                    self._add_to_logs(line)
        except Exception as e:
            raise exc.AirbyteConnectorReadError(
                log_text=self._last_log_messages,
            ) from e

    def _tally_records(
        self,
        messages: Iterable[AirbyteMessage],
    ) -> Generator[AirbyteMessage, Any, None]:
        """This method simply tallies the number of records processed and yields the messages."""
        self._processed_records = 0  # Reset the counter before we start
        progress.reset(len(self._selected_stream_names or []))

        for message in messages:
            yield message
            progress.log_records_read(self._processed_records)

    def read(
        self,
        cache: SQLCacheBase | None = None,
        *,
        write_strategy: str | WriteStrategy = WriteStrategy.AUTO,
        force_full_refresh: bool = False,
    ) -> ReadResult:
        """Read from the connector and write to the cache.

        Args:
            cache: The cache to write to. If None, a default cache will be used.
            write_strategy: The strategy to use when writing to the cache. If a string, it must be
                one of "append", "upsert", "replace", or "auto". If a WriteStrategy, it must be one
                of WriteStrategy.APPEND, WriteStrategy.UPSERT, WriteStrategy.REPLACE, or
                WriteStrategy.AUTO.
            force_full_refresh: If True, the source will operate in full refresh mode. Otherwise,
                streams will be read in incremental mode if supported by the connector. This option
                must be True when using the "replace" strategy.
        """
        if write_strategy == WriteStrategy.REPLACE and not force_full_refresh:
            raise exc.AirbyteLibInputError(
                message="The replace strategy requires full refresh mode.",
                context={
                    "write_strategy": write_strategy,
                    "force_full_refresh": force_full_refresh,
                },
            )
        if cache is None:
            cache = get_default_cache()

        if isinstance(write_strategy, str):
            try:
                write_strategy = WriteStrategy(write_strategy)
            except ValueError:
                raise exc.AirbyteLibInputError(
                    message="Invalid strategy",
                    context={
                        "write_strategy": write_strategy,
                        "available_strategies": [s.value for s in WriteStrategy],
                    },
                ) from None

        if not self._selected_stream_names:
            raise exc.AirbyteLibNoStreamsSelectedError(
                connector_name=self.name,
                available_streams=self.get_available_streams(),
            )

        cache.register_source(
            source_name=self.name,
            incoming_source_catalog=self.configured_catalog,
            stream_names=set(self._selected_stream_names),
        )
        state = cache.get_state() if not force_full_refresh else None
        print(f"Started `{self.name}` read operation at {pendulum.now().format('HH:mm:ss')}...")
        cache.process_airbyte_messages(
            self._tally_records(
                self._read(
                    cache.get_telemetry_info(),
                    state=state,
                ),
            ),
            write_strategy=write_strategy,
        )
        print(f"Completed `{self.name}` read operation at {pendulum.now().format('HH:mm:ss')}.")

        return ReadResult(
            processed_records=self._processed_records,
            cache=cache,
            processed_streams=[stream.stream.name for stream in self.configured_catalog.streams],
        )
