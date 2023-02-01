#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import logging
from typing import Any, Iterable, List, Mapping, Tuple

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import AirbyteCatalog
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

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
                            f"{base_name}/{SchemaHelpers.clean_name(table.get('name'))}",
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
