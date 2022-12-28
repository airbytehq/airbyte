#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import logging
from typing import Any, Iterable, List, Mapping, Tuple

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import AirbyteCatalog
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator

from .helpers import Helpers
from .streams import AirtableBases, AirtableStream, AirtableTables


class SourceAirtable(AbstractSource):

    logger: logging.Logger = logging.getLogger("airbyte")
    streams_catalog: Iterable[Mapping[str, Any]] = []

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        auth = TokenAuthenticator(token=config["api_key"])
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

    def prepare_catalog_for_base(self, base_id: str, base_name: str, base_tables: list) -> Iterable[Mapping[str, Any]]:
        for table in base_tables:
            if table not in self.streams_catalog:
                self.streams_catalog.append(
                    {
                        "stream_path": f"{base_id}/{table.get('id')}",
                        "stream": Helpers.get_airbyte_stream(
                            f"{base_name}/{Helpers.clean_name(table.get('name'))}",
                            Helpers.get_json_schema(table),
                        ),
                    }
                )

    def discover(self, logger: AirbyteLogger, config) -> AirbyteCatalog:
        """
        Override to provide the dynamic schema generation capabilities,
        using resource available for authenticated user.

        Retrieve: Bases, Tables from each Base, generate JSON Schema for each table.
        """
        auth = TokenAuthenticator(token=config["api_key"])

        # list all bases available for authenticated account
        for base in AirtableBases(authenticator=auth).read_records(sync_mode=None):
            # list and process each table under each base to generate the JSON Schema
            self.prepare_catalog_for_base(
                base_id=base.get("id"),
                base_name=Helpers.clean_name(base.get("name")),
                base_tables=list(AirtableTables(base_id=base.get("id"), authenticator=auth).read_records(sync_mode=None)),
            )
        return AirbyteCatalog(streams=[stream["stream"] for stream in self.streams_catalog])

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        if not self.streams_catalog:
            self.discover(None, config)

        for stream in self.streams_catalog:
            yield AirtableStream(
                stream_path=stream["stream_path"],
                stream_name=stream["stream"].name,
                stream_schema=stream["stream"].json_schema,
                authenticator=TokenAuthenticator(token=config["api_key"]),
            )
