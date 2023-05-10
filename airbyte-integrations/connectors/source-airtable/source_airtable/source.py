#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
from typing import Any, Iterable, Iterator, List, Mapping, MutableMapping, Tuple, Union

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import AirbyteCatalog, AirbyteMessage, AirbyteStateMessage, AirbyteStreamStatus, ConfiguredAirbyteCatalog
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.utils.schema_helpers import split_config
from airbyte_cdk.utils.event_timing import create_timer
from airbyte_cdk.utils.stream_status_utils import as_airbyte_message as stream_status_as_airbyte_message
from airbyte_cdk.utils.traced_exception import AirbyteTracedException

from .auth import AirtableAuth
from .schema_helpers import SchemaHelpers
from .streams import AirtableBases, AirtableStream, AirtableTables


class SourceAirtable(AbstractSource):

    logger: logging.Logger = logging.getLogger("airbyte")
    streams_catalog: Iterable[Mapping[str, Any]] = []
    _auth: AirtableAuth = None

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        auth = AirtableAuth(config)
        try:
            # try reading first table from each base, to check the connectivity,
            for base in AirtableBases(authenticator=auth).read_records(sync_mode=None):
                base_id = base.get("id")
                base_name = base.get("name")
                self.logger.info(f"Reading first table info for base: {base_name}")
                next(AirtableTables(base_id=base_id, authenticator=auth).read_records(sync_mode=None))
            return True, None
        except Exception as e:
            return False, str(e)

    def read(
        self,
        logger: logging.Logger,
        config: Mapping[str, Any],
        catalog: ConfiguredAirbyteCatalog,
        state: Union[List[AirbyteStateMessage], MutableMapping[str, Any]] = None,
    ) -> Iterator[AirbyteMessage]:
        """Implements the Read operation from the Airbyte Specification. See https://docs.airbyte.com/understanding-airbyte/airbyte-protocol/."""
        logger.info(f"Starting syncing {self.name}")
        config, internal_config = split_config(config)
        # TODO assert all streams exist in the connector
        # get the streams once in case the connector needs to make any queries to generate them
        stream_instances = {s.name: s for s in self.streams(config)}
        state_manager = ConnectorStateManager(stream_instance_map=stream_instances, state=state)
        self._stream_to_instance_map = stream_instances
        with create_timer(self.name) as timer:
            for configured_stream in catalog.streams:
                stream_instance = stream_instances.get(configured_stream.stream.name)
                if not stream_instance:
                    table_id = configured_stream.stream.name.split("/")[2]
                    similar_streams = [s for s in stream_instances if s.endswith(table_id)]
                    logger.warn(
                        f"The requested stream {configured_stream.stream.name} was not found in the source. Please check if this stream was renamed or removed previously and reset data, skipping it for now. For more information please refer to documentation: https://docs.airbyte.com/integrations/sources/airtable/#note-on-changed-table-names"
                        f" Similar streams: {similar_streams}"
                        f" Available streams: {stream_instances.keys()}"
                    )
                    continue
                stream_is_available, error = stream_instance.check_availability(logger, self)
                if not stream_is_available:
                    logger.warning(f"Skipped syncing stream '{stream_instance.name}' because it was unavailable. Error: {error}")
                    continue
                try:
                    timer.start_event(f"Syncing stream {configured_stream.stream.name}")
                    logger.info(f"Marking stream {configured_stream.stream.name} as STARTED")
                    yield stream_status_as_airbyte_message(configured_stream, AirbyteStreamStatus.STARTED)
                    yield from self._read_stream(
                        logger=logger,
                        stream_instance=stream_instance,
                        configured_stream=configured_stream,
                        state_manager=state_manager,
                        internal_config=internal_config,
                    )
                    logger.info(f"Marking stream {configured_stream.stream.name} as STOPPED")
                    yield stream_status_as_airbyte_message(configured_stream, AirbyteStreamStatus.COMPLETE)
                except AirbyteTracedException as e:
                    yield stream_status_as_airbyte_message(configured_stream, AirbyteStreamStatus.INCOMPLETE)
                    raise e
                except Exception as e:
                    logger.exception(f"Encountered an exception while reading stream {configured_stream.stream.name}")
                    logger.info(f"Marking stream {configured_stream.stream.name} as STOPPED")
                    yield stream_status_as_airbyte_message(configured_stream, AirbyteStreamStatus.INCOMPLETE)
                    display_message = stream_instance.get_error_display_message(e)
                    if display_message:
                        raise AirbyteTracedException.from_exception(e, message=display_message) from e
                    raise e
                finally:
                    timer.finish_event()
                    logger.info(f"Finished syncing {configured_stream.stream.name}")
                    logger.info(timer.report())

        logger.info(f"Finished syncing {self.name}")

    def discover(self, logger: AirbyteLogger, config) -> AirbyteCatalog:
        """
        Override to provide the dynamic schema generation capabilities,
        using resource available for authenticated user.

        Retrieve: Bases, Tables from each Base, generate JSON Schema for each table.
        """
        auth = self._auth or AirtableAuth(config)
        # list all bases available for authenticated account
        for base in AirtableBases(authenticator=auth).read_records(sync_mode=None):
            base_id = base.get("id")
            base_name = SchemaHelpers.clean_name(base.get("name"))
            # list and process each table under each base to generate the JSON Schema
            for table in list(AirtableTables(base_id, authenticator=auth).read_records(sync_mode=None)):
                self.streams_catalog.append(
                    {
                        "stream_path": f"{base_id}/{table.get('id')}",
                        "stream": SchemaHelpers.get_airbyte_stream(
                            f"{base_name}/{SchemaHelpers.clean_name(table.get('name'))}/{table.get('id')}",
                            SchemaHelpers.get_json_schema(table),
                        ),
                    }
                )
        return AirbyteCatalog(streams=[stream["stream"] for stream in self.streams_catalog])

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        self._auth = AirtableAuth(config)
        # trigger discovery to populate the streams_catalog
        if not self.streams_catalog:
            self.discover(None, config)
        # build the stream class from prepared streams_catalog
        for stream in self.streams_catalog:
            yield AirtableStream(
                stream_path=stream["stream_path"],
                stream_name=stream["stream"].name,
                stream_schema=stream["stream"].json_schema,
                authenticator=self._auth,
            )
