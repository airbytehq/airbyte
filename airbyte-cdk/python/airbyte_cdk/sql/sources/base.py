# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
"""Base class implementation for sources."""

from __future__ import annotations

import json
import warnings
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

import yaml
from rich import print  # noqa: A004  # Allow shadowing the built-in
from rich.syntax import Syntax

from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteMessage,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
    Type,
)

from airbyte_cdk.sql import exceptions as exc
from airbyte_cdk.sql._connector_base import ConnectorBase
from airbyte_cdk.sql._message_iterators import AirbyteMessageIterator
from airbyte_cdk.sql.temp_files import as_temp_files
from airbyte_cdk.sql.caches.util import get_default_cache
from airbyte_cdk.sql.datasets._lazy import LazyDataset
from airbyte_cdk.sql.progress import ProgressStyle, ProgressTracker
from airbyte_cdk.sql.records import StreamRecord, StreamRecordHandler
from airbyte_cdk.sql.results import ReadResult
from airbyte_cdk.sql.catalog_providers import CatalogProvider
from airbyte_cdk.sql.strategies import WriteStrategy


if TYPE_CHECKING:
    from collections.abc import Generator, Iterable, Iterator

    from airbyte_cdk import ConnectorSpecification
    from airbyte_cdk.models import AirbyteStream

    from airbyte_cdk.sql._executors.base import Executor
    from airbyte_cdk.sql.caches import CacheBase
    from airbyte_cdk.sql.documents import Document
    from airbyte_cdk.sql.state_providers import StateProviderBase
    from airbyte_cdk.sql.state_writers import StateWriterBase


class Source(ConnectorBase):
    """A class representing a source that can be called."""

    connector_type: Literal["source"] = "source"

    def __init__(
        self,
        executor: Executor,
        name: str,
        config: dict[str, Any] | None = None,
        streams: str | list[str] | None = None,
        *,
        validate: bool = False,
    ) -> None:
        """Initialize the source.

        If config is provided, it will be validated against the spec if validate is True.
        """
        self._to_be_selected_streams: list[str] | str = []
        """Used to hold selection criteria before catalog is known."""

        super().__init__(
            executor=executor,
            name=name,
            config=config,
            validate=validate,
        )
        self._config_dict: dict[str, Any] | None = None
        self._last_log_messages: list[str] = []
        self._discovered_catalog: AirbyteCatalog | None = None
        self._selected_stream_names: list[str] = []
        if config is not None:
            self.set_config(config, validate=validate)
        if streams is not None:
            self.select_streams(streams)

        self._deployed_api_root: str | None = None
        self._deployed_workspace_id: str | None = None
        self._deployed_source_id: str | None = None

    def set_streams(self, streams: list[str]) -> None:
        """Deprecated. See select_streams()."""
        warnings.warn(
            "The 'set_streams' method is deprecated and will be removed in a future version. "
            "Please use the 'select_streams' method instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.select_streams(streams)

    def _log_warning_preselected_stream(self, streams: str | list[str]) -> None:
        """Logs a warning message indicating stream selection which are not selected yet."""
        if streams == "*":
            print(
                "Warning: Config is not set yet. All streams will be selected after config is set."
            )
        else:
            print(
                "Warning: Config is not set yet. "
                f"Streams to be selected after config is set: {streams}"
            )

    def select_all_streams(self) -> None:
        """Select all streams.

        This is a more streamlined equivalent to:
        > source.select_streams(source.get_available_streams()).
        """
        if self._config_dict is None:
            self._to_be_selected_streams = "*"
            self._log_warning_preselected_stream(self._to_be_selected_streams)
            return

        self._selected_stream_names = self.get_available_streams()

    def select_streams(self, streams: str | list[str]) -> None:
        """Select the stream names that should be read from the connector.

        Args:
            streams: A list of stream names to select. If set to "*", all streams will be selected.

        Currently, if this is not set, all streams will be read.
        """
        if self._config_dict is None:
            self._to_be_selected_streams = streams
            self._log_warning_preselected_stream(streams)
            return

        if streams == "*":
            self.select_all_streams()
            return

        if isinstance(streams, str):
            # If a single stream is provided, convert it to a one-item list
            streams = [streams]

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
        validate: bool = True,
    ) -> None:
        """Set the config for the connector.

        If validate is True, raise an exception if the config fails validation.

        If validate is False, validation will be deferred until check() or validate_config()
        is called.
        """
        if validate:
            self.validate_config(config)

        self._config_dict = config

        if self._to_be_selected_streams:
            self.select_streams(self._to_be_selected_streams)
            self._to_be_selected_streams = []

    def get_config(self) -> dict[str, Any]:
        """Get the config for the connector."""
        return self._config

    @property
    def _config(self) -> dict[str, Any]:
        if self._config_dict is None:
            raise exc.AirbyteConnectorConfigurationMissingError(
                connector_name=self.name,
                guidance="Provide via get_source() or set_config()",
            )
        return self._config_dict

    def _discover(self) -> AirbyteCatalog:
        """Call discover on the connector.

        This involves the following steps:
        - Write the config to a temporary file
        - execute the connector with discover --config <config_file>
        - Listen to the messages and return the first AirbyteCatalog that comes along.
        - Make sure the subprocess is killed when the function returns.
        """
        with as_temp_files([self._config]) as [config_file]:
            for msg in self._execute(["discover", "--config", config_file]):
                if msg.type == Type.CATALOG and msg.catalog:
                    return msg.catalog
            raise exc.AirbyteConnectorMissingCatalogError(
                connector_name=self.name,
                log_text=self._last_log_messages,
            )

    def get_available_streams(self) -> list[str]:
        """Get the available streams from the spec."""
        return [s.name for s in self.discovered_catalog.streams]

    def _get_incremental_stream_names(self) -> list[str]:
        """Get the name of streams that support incremental sync."""
        return [
            stream.name
            for stream in self.discovered_catalog.streams
            if SyncMode.incremental in stream.supported_sync_modes
        ]

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
            connector_name=self.name,
            log_text=self._last_log_messages,
        )

    @property
    def config_spec(self) -> dict[str, Any]:
        """Generate a configuration spec for this connector, as a JSON Schema definition.

        This function generates a JSON Schema dictionary with configuration specs for the
        current connector, as a dictionary.

        Returns:
            dict: The JSON Schema configuration spec as a dictionary.
        """
        return self._get_spec(force_refresh=True).connectionSpecification

    def print_config_spec(
        self,
        format: Literal["yaml", "json"] = "yaml",  # noqa: A002
        *,
        output_file: Path | str | None = None,
    ) -> None:
        """Print the configuration spec for this connector.

        Args:
            format: The format to print the spec in. Must be "yaml" or "json".
            output_file: Optional. If set, the spec will be written to the given file path.
                Otherwise, it will be printed to the console.
        """
        if format not in {"yaml", "json"}:
            raise exc.AirbyteInputError(
                message="Invalid format. Expected 'yaml' or 'json'",
                input_value=format,
            )
        if isinstance(output_file, str):
            output_file = Path(output_file)

        if format == "yaml":
            content = yaml.dump(self.config_spec, indent=2)
        elif format == "json":
            content = json.dumps(self.config_spec, indent=2)

        if output_file:
            output_file.write_text(content)
            return

        syntax_highlighted = Syntax(content, format)
        print(syntax_highlighted)

    @property
    def _yaml_spec(self) -> str:
        """Get the spec as a yaml string.

        For now, the primary use case is for writing and debugging a valid config for a source.

        This is private for now because we probably want better polish before exposing this
        as a stable interface. This will also get easier when we have docs links with this info
        for each connector.
        """
        spec_obj: ConnectorSpecification = self._get_spec()
        spec_dict: dict[str, Any] = spec_obj.model_dump(exclude_unset=True)
        # convert to a yaml string
        return yaml.dump(spec_dict)

    @property
    def docs_url(self) -> str:
        """Get the URL to the connector's documentation."""
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
        return self.get_configured_catalog(streams=streams_filter)

    def get_configured_catalog(
        self,
        streams: Literal["*"] | list[str] | None = None,
    ) -> ConfiguredAirbyteCatalog:
        """Get a configured catalog for the given streams.

        If no streams are provided, the selected streams will be used. If no streams are selected,
        all available streams will be used.

        If '*' is provided, all available streams will be used.
        """
        selected_streams: list[str] = []
        if streams is None:
            selected_streams = self._selected_stream_names or self.get_available_streams()
        elif streams == "*":
            selected_streams = self.get_available_streams()
        elif isinstance(streams, list):
            selected_streams = streams
        else:
            raise exc.AirbyteInputError(
                message="Invalid streams argument.",
                input_value=streams,
            )

        return ConfiguredAirbyteCatalog(
            streams=[
                ConfiguredAirbyteStream(
                    stream=stream,
                    destination_sync_mode=DestinationSyncMode.overwrite,
                    primary_key=stream.source_defined_primary_key,
                    sync_mode=SyncMode.incremental,
                )
                for stream in self.discovered_catalog.streams
                if stream.name in selected_streams
            ],
        )

    def get_stream_json_schema(self, stream_name: str) -> dict[str, Any]:
        """Return the JSON Schema spec for the specified stream name."""
        catalog: AirbyteCatalog = self.discovered_catalog
        found: list[AirbyteStream] = [
            stream for stream in catalog.streams if stream.name == stream_name
        ]

        if len(found) == 0:
            raise exc.AirbyteInputError(
                message="Stream name does not exist in catalog.",
                input_value=stream_name,
            )

        if len(found) > 1:
            raise exc.AirbyteInternalError(
                message="Duplicate streams found with the same name.",
                context={
                    "found_streams": found,
                },
            )

        return found[0].json_schema

    def get_records(
        self,
        stream: str,
        *,
        normalize_field_names: bool = False,
        prune_undeclared_fields: bool = True,
    ) -> LazyDataset:
        """Read a stream from the connector.

        Args:
            stream: The name of the stream to read.
            normalize_field_names: When `True`, field names will be normalized to lower case, with
                special characters removed. This matches the behavior of Airbyte caches and most
                Airbyte destinations.
            prune_undeclared_fields: When `True`, undeclared fields will be pruned from the records,
                which generally matches the behavior of Airbyte caches and most Airbyte
                destinations, specifically when you expect the catalog may be stale. You can disable
                this to keep all fields in the records.

        This involves the following steps:
        * Call discover to get the catalog
        * Generate a configured catalog that syncs the given stream in full_refresh mode
        * Write the configured catalog and the config to a temporary file
        * execute the connector with read --config <config_file> --catalog <catalog_file>
        * Listen to the messages and return the first AirbyteRecordMessages that come along.
        * Make sure the subprocess is killed when the function returns.
        """
        discovered_catalog: AirbyteCatalog = self.discovered_catalog
        configured_catalog = ConfiguredAirbyteCatalog(
            streams=[
                ConfiguredAirbyteStream(
                    stream=s,
                    sync_mode=SyncMode.full_refresh,
                    destination_sync_mode=DestinationSyncMode.overwrite,
                )
                for s in discovered_catalog.streams
                if s.name == stream
            ],
        )
        if len(configured_catalog.streams) == 0:
            raise exc.AirbyteInputError(
                message="Requested stream does not exist.",
                context={
                    "stream": stream,
                    "available_streams": self.get_available_streams(),
                    "connector_name": self.name,
                },
            ) from KeyError(stream)

        configured_stream = configured_catalog.streams[0]

        def _with_logging(records: Iterable[dict[str, Any]]) -> Iterator[dict[str, Any]]:
            yield from records

        stream_record_handler = StreamRecordHandler(
            json_schema=self.get_stream_json_schema(stream),
            prune_extra_fields=prune_undeclared_fields,
            normalize_keys=normalize_field_names,
        )

        # This method is non-blocking, so we use "PLAIN" to avoid a live progress display
        progress_tracker = ProgressTracker(
            ProgressStyle.PLAIN,
            source=self,
            cache=None,
            destination=None,
            expected_streams=[stream],
        )

        iterator: Iterator[dict[str, Any]] = (
            StreamRecord.from_record_message(
                record_message=record.record,
                stream_record_handler=stream_record_handler,
            )
            for record in self._read_with_catalog(
                catalog=configured_catalog,
                progress_tracker=progress_tracker,
            )
            if record.record
        )
        progress_tracker.log_success()
        return LazyDataset(
            iterator,
            stream_metadata=configured_stream,
        )

    def get_documents(
        self,
        stream: str,
        title_property: str | None = None,
        content_properties: list[str] | None = None,
        metadata_properties: list[str] | None = None,
        *,
        render_metadata: bool = False,
    ) -> Iterable[Document]:
        """Read a stream from the connector and return the records as documents.

        If metadata_properties is not set, all properties that are not content will be added to
        the metadata.

        If render_metadata is True, metadata will be rendered in the document, as well as the
        the main content.
        """
        return self.get_records(stream).to_documents(
            title_property=title_property,
            content_properties=content_properties,
            metadata_properties=metadata_properties,
            render_metadata=render_metadata,
        )

    def _get_airbyte_message_iterator(
        self,
        *,
        streams: Literal["*"] | list[str] | None = None,
        state_provider: StateProviderBase | None = None,
        progress_tracker: ProgressTracker,
        force_full_refresh: bool = False,
    ) -> AirbyteMessageIterator:
        """Get an AirbyteMessageIterator for this source."""
        return AirbyteMessageIterator(
            self._read_with_catalog(
                catalog=self.get_configured_catalog(streams=streams),
                state=state_provider if not force_full_refresh else None,
                progress_tracker=progress_tracker,
            )
        )

    def _read_with_catalog(
        self,
        catalog: ConfiguredAirbyteCatalog,
        progress_tracker: ProgressTracker,
        state: StateProviderBase | None = None,
    ) -> Generator[AirbyteMessage, None, None]:
        """Call read on the connector.

        This involves the following steps:
        * Write the config to a temporary file
        * execute the connector with read --config <config_file> --catalog <catalog_file>
        * Listen to the messages and return the AirbyteRecordMessages that come along.
        * Send out telemetry on the performed sync (with information about which source was used and
          the type of the cache)
        """
        with as_temp_files(
            [
                self._config,
                catalog.model_dump_json(),
                state.to_state_input_file_text() if state else "[]",
            ]
        ) as [
            config_file,
            catalog_file,
            state_file,
        ]:
            message_generator = self._execute(
                [
                    "read",
                    "--config",
                    config_file,
                    "--catalog",
                    catalog_file,
                    "--state",
                    state_file,
                ],
                progress_tracker=progress_tracker,
            )
            yield from progress_tracker.tally_records_read(message_generator)
        progress_tracker.log_read_complete()

    def _peek_airbyte_message(
        self,
        message: AirbyteMessage,
        *,
        raise_on_error: bool = True,
    ) -> None:
        """Process an Airbyte message.

        This method handles reading Airbyte messages and taking action, if needed, based on the
        message type. For instance, log messages are logged, records are tallied, and errors are
        raised as exceptions if `raise_on_error` is True.

        Raises:
            AirbyteConnectorFailedError: If a TRACE message of type ERROR is emitted.
        """
        super()._peek_airbyte_message(message, raise_on_error=raise_on_error)

    def _log_incremental_streams(
        self,
        *,
        incremental_streams: set[str] | None = None,
    ) -> None:
        """Log the streams which are using incremental sync mode."""
        log_message = (
            "The following streams are currently using incremental sync:\n"
            f"{incremental_streams}\n"
            "To perform a full refresh, set 'force_full_refresh=True' in 'airbyte.read()' method."
        )
        print(log_message)

    def read(
        self,
        cache: CacheBase | None = None,
        *,
        streams: str | list[str] | None = None,
        write_strategy: str | WriteStrategy = WriteStrategy.AUTO,
        force_full_refresh: bool = False,
        skip_validation: bool = False,
    ) -> ReadResult:
        """Read from the connector and write to the cache.

        Args:
            cache: The cache to write to. If not set, a default cache will be used.
            streams: Optional if already set. A list of stream names to select for reading. If set
                to "*", all streams will be selected.
            write_strategy: The strategy to use when writing to the cache. If a string, it must be
                one of "append", "upsert", "replace", or "auto". If a WriteStrategy, it must be one
                of WriteStrategy.APPEND, WriteStrategy.UPSERT, WriteStrategy.REPLACE, or
                WriteStrategy.AUTO.
            force_full_refresh: If True, the source will operate in full refresh mode. Otherwise,
                streams will be read in incremental mode if supported by the connector. This option
                must be True when using the "replace" strategy.
            skip_validation: If True, Airbyte will not pre-validate the input configuration before
                running the connector. This can be helpful in debugging, when you want to send
                configurations to the connector that otherwise might be rejected by JSON Schema
                validation rules.
        """
        cache = cache or get_default_cache()
        progress_tracker = ProgressTracker(
            source=self,
            cache=cache,
            destination=None,
            expected_streams=None,  # Will be set later
        )

        # Set up state provider if not in full refresh mode
        if force_full_refresh:
            state_provider: StateProviderBase | None = None
        else:
            state_provider = cache.get_state_provider(
                source_name=self._name,
            )
        state_writer = cache.get_state_writer(source_name=self._name)

        if streams:
            self.select_streams(streams)

        if not self._selected_stream_names:
            raise exc.AirbyteNoStreamsSelectedError(
                connector_name=self.name,
                available_streams=self.get_available_streams(),
            )

        try:
            result = self._read_to_cache(
                cache=cache,
                catalog_provider=CatalogProvider(self.configured_catalog),
                stream_names=self._selected_stream_names,
                state_provider=state_provider,
                state_writer=state_writer,
                write_strategy=write_strategy,
                force_full_refresh=force_full_refresh,
                skip_validation=skip_validation,
                progress_tracker=progress_tracker,
            )
        except exc.AirbyteInternalError as ex:
            progress_tracker.log_failure(exception=ex)
            raise exc.AirbyteConnectorFailedError(
                connector_name=self.name,
                log_text=self._last_log_messages,
            ) from ex
        except Exception as ex:
            progress_tracker.log_failure(exception=ex)
            raise

        progress_tracker.log_success()
        return result

    def _read_to_cache(  # noqa: PLR0913  # Too many arguments
        self,
        cache: CacheBase,
        *,
        catalog_provider: CatalogProvider,
        stream_names: list[str],
        state_provider: StateProviderBase | None,
        state_writer: StateWriterBase | None,
        write_strategy: str | WriteStrategy = WriteStrategy.AUTO,
        force_full_refresh: bool = False,
        skip_validation: bool = False,
        progress_tracker: ProgressTracker,
    ) -> ReadResult:
        """Internal read method."""
        if write_strategy == WriteStrategy.REPLACE and not force_full_refresh:
            warnings.warn(
                message=(
                    "Using `REPLACE` strategy without also setting `full_refresh_mode=True` "
                    "could result in data loss. "
                    "To silence this warning, use the following: "
                    'warnings.filterwarnings("ignore", '
                    'category="airbyte.warnings.AirbyteDataLossWarning")`'
                ),
                category=exc.AirbyteDataLossWarning,
                stacklevel=1,
            )
        if isinstance(write_strategy, str):
            try:
                write_strategy = WriteStrategy(write_strategy)
            except ValueError:
                raise exc.AirbyteInputError(
                    message="Invalid strategy",
                    context={
                        "write_strategy": write_strategy,
                        "available_strategies": [s.value for s in WriteStrategy],
                    },
                ) from None

        # Run optional validation step
        if not skip_validation:
            self.validate_config()

        # Log incremental stream if incremental streams are known
        if state_provider and state_provider.known_stream_names:
            # Retrieve set of the known streams support which support incremental sync
            incremental_streams = (
                set(self._get_incremental_stream_names())
                & state_provider.known_stream_names
                & set(self.get_selected_streams())
            )
            if incremental_streams:
                self._log_incremental_streams(incremental_streams=incremental_streams)

        airbyte_message_iterator = AirbyteMessageIterator(
            self._read_with_catalog(
                catalog=catalog_provider.configured_catalog,
                state=state_provider,
                progress_tracker=progress_tracker,
            )
        )
        cache._write_airbyte_message_stream(  # noqa: SLF001  # Non-public API
            stdin=airbyte_message_iterator,
            catalog_provider=catalog_provider,
            write_strategy=write_strategy,
            state_writer=state_writer,
            progress_tracker=progress_tracker,
        )

        # Flush the WAL, if applicable
        cache.processor._do_checkpoint()  # noqa: SLF001  # Non-public API

        return ReadResult(
            source_name=self.name,
            progress_tracker=progress_tracker,
            processed_streams=stream_names,
            cache=cache,
        )


__all__ = [
    "Source",
]
