import logging
from typing import Any, List, Mapping, Optional, Tuple

from airbyte_protocol_dataclasses.models import (
    AirbyteCatalog,
    Status,
)
from fastapi import HTTPException

from airbyte_cdk.connector_builder.models import StreamRead
from airbyte_cdk.connector_builder.test_reader import TestReader
from airbyte_cdk.entrypoint import AirbyteEntrypoint
from airbyte_cdk.models import (
    AirbyteStateMessage,
    ConfiguredAirbyteCatalog,
)
from airbyte_cdk.sources.declarative.concurrent_declarative_source import (
    ConcurrentDeclarativeSource,
)
from airbyte_cdk.test.entrypoint_wrapper import AirbyteEntrypointException, EntrypointOutput


class ManifestCommandProcessor:
    _source: ConcurrentDeclarativeSource
    _logger = logging.getLogger("airbyte.manifest-server")

    def __init__(self, source: ConcurrentDeclarativeSource) -> None:
        self._source = source

    def test_read(
        self,
        config: Mapping[str, Any],
        catalog: ConfiguredAirbyteCatalog,
        state: List[AirbyteStateMessage],
        record_limit: int,
        page_limit: int,
        slice_limit: int,
    ) -> StreamRead:
        """
        Test the read method of the source.
        """
        test_read_handler = TestReader(
            max_pages_per_slice=page_limit,
            max_slices=slice_limit,
            max_record_limit=record_limit,
        )

        stream_read = test_read_handler.run_test_read(
            source=self._source,
            config=config,
            configured_catalog=catalog,
            state=state,
            stream_name=catalog.streams[0].stream.name,
            record_limit=record_limit,
        )

        return stream_read

    def check_connection(
        self,
        config: Mapping[str, Any],
    ) -> Tuple[bool, Optional[str]]:
        """
        Check the connection to the source.
        """

        spec = self._source.spec(self._logger)
        entrypoint = AirbyteEntrypoint(source=self._source)
        messages = entrypoint.check(spec, config)
        output = EntrypointOutput(
            messages=[AirbyteEntrypoint.airbyte_message_to_string(m) for m in messages],
            command=["check"],
        )
        self._raise_on_trace_message(output)

        status_messages = output.connection_status_messages
        if not status_messages or status_messages[-1].connectionStatus is None:
            return False, "Connection check did not return a status message"

        connection_status = status_messages[-1].connectionStatus
        return (
            connection_status.status == Status.SUCCEEDED,
            connection_status.message,
        )

    def discover(
        self,
        config: Mapping[str, Any],
    ) -> Optional[AirbyteCatalog]:
        """
        Discover the catalog from the source.
        """
        spec = self._source.spec(self._logger)
        entrypoint = AirbyteEntrypoint(source=self._source)
        messages = entrypoint.discover(spec, config)
        output = EntrypointOutput(
            messages=[AirbyteEntrypoint.airbyte_message_to_string(m) for m in messages],
            command=["discover"],
        )
        self._raise_on_trace_message(output)

        try:
            catalog_message = output.catalog
            return catalog_message.catalog
        except ValueError:
            # No catalog message found
            return None

    def _raise_on_trace_message(
        self,
        output: EntrypointOutput,
    ) -> None:
        """
        Raise an exception if a trace message is found.
        """
        try:
            output.raise_if_errors()
        except AirbyteEntrypointException as e:
            raise HTTPException(status_code=422, detail=e.message)
