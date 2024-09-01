#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import logging
from typing import Any, Iterable, Iterator, List, Mapping, MutableMapping, Tuple, Union

from airbyte_cdk.models import AirbyteCatalog, AirbyteMessage, AirbyteStateMessage, ConfiguredAirbyteCatalog
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.utils.schema_helpers import split_config
from airbyte_protocol.models import SyncMode

from .auth import AirtableAuth
from .schema_helpers import SchemaHelpers
from .streams import AirtableBases, AirtableStream, AirtableTables


class SourceAirtable(AbstractSource):

    logger: logging.Logger = logging.getLogger("airbyte")
    streams_catalog: Iterable[Mapping[str, Any]] = []
    _auth: AirtableAuth = None

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        auth = AirtableAuth(config)
        try:
            # try reading first table from each base, to check the connectivity,
            for base in AirtableBases(authenticator=auth).read_records(sync_mode=SyncMode.full_refresh):
                base_id = base.get("id")
                base_name = base.get("name")
                self.logger.info(f"Reading first table info for base: {base_name}")
                next(AirtableTables(base_id=base_id, authenticator=auth).read_records(sync_mode=SyncMode.full_refresh))
            return True, None
        except Exception as e:
            return False, str(e)

    def _remove_missed_streams_from_catalog(
        self, logger: logging.Logger, config: Mapping[str, Any], catalog: ConfiguredAirbyteCatalog
    ) -> ConfiguredAirbyteCatalog:
        config, _ = split_config(config)
        stream_instances = {s.name: s for s in self.streams(config)}
        for index, configured_stream in enumerate(catalog.streams):
            stream_instance = stream_instances.get(configured_stream.stream.name)
            if not stream_instance:
                table_id = configured_stream.stream.name.split("/")[2]
                similar_streams = [s for s in stream_instances if s.endswith(table_id)]
                logger.warning(
                    f"The requested stream {configured_stream.stream.name} was not found in the source. Please check if this stream was renamed or removed previously and reset data, removing from catalog for this sync run. For more information please refer to documentation: https://docs.airbyte.com/integrations/sources/airtable/#note-on-changed-table-names-and-deleted-tables"
                    f" Similar streams: {similar_streams}"
                    f" Available streams: {stream_instances.keys()}"
                )
                del catalog.streams[index]
        return catalog

    def read(
        self,
        logger: logging.Logger,
        config: Mapping[str, Any],
        catalog: ConfiguredAirbyteCatalog,
        state: Union[List[AirbyteStateMessage], MutableMapping[str, Any]] = None,
    ) -> Iterator[AirbyteMessage]:
        """Override to provide filtering of catalog in case if streams were renamed/removed previously"""
        catalog = self._remove_missed_streams_from_catalog(logger, config, catalog)
        return super().read(logger, config, catalog, state)

    def discover(self, logger: logging.Logger, config) -> AirbyteCatalog:
        """
        Override to provide the dynamic schema generation capabilities,
        using resource available for authenticated user.

        Retrieve: Bases, Tables from each Base, generate JSON Schema for each table.
        """
        auth = self._auth or AirtableAuth(config)
        # list all bases available for authenticated account
        for base in AirtableBases(authenticator=auth).read_records(sync_mode=SyncMode.full_refresh):
            base_id = base.get("id")
            base_name = SchemaHelpers.clean_name(base.get("name"))
            # list and process each table under each base to generate the JSON Schema
            for table in AirtableTables(base_id, authenticator=auth).read_records(sync_mode=SyncMode.full_refresh):
                self.streams_catalog.append(
                    {
                        "stream_path": f"{base_id}/{table.get('id')}",
                        "stream": SchemaHelpers.get_airbyte_stream(
                            f"{base_name}/{SchemaHelpers.clean_name(table.get('name'))}/{table.get('id')}",
                            SchemaHelpers.get_json_schema(table),
                        ),
                        "table_name": table.get("name"),
                    }
                )
        return AirbyteCatalog(streams=[stream["stream"] for stream in self.streams_catalog])

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        The Discover method is triggered during each synchronization to fetch all available streams (tables).
        If a stream becomes unavailable, an ERROR message will be printed in the logs.
        """
        self._auth = AirtableAuth(config)
        if not self.streams_catalog:
            self.discover(None, config)
        for stream in self.streams_catalog:
            yield AirtableStream(
                stream_path=stream["stream_path"],
                stream_name=stream["stream"].name,
                stream_schema=stream["stream"].json_schema,
                table_name=stream["table_name"],
                authenticator=self._auth,
            )
