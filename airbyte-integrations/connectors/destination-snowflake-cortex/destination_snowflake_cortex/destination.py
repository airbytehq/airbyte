#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import os
from typing import Any, Iterable, Mapping, Optional

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.destinations import Destination
from airbyte_cdk.destinations.vector_db_based.embedder import Embedder, create_from_config
from airbyte_cdk.destinations.vector_db_based.indexer import Indexer
from airbyte_cdk.destinations.vector_db_based.writer import Writer
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, ConfiguredAirbyteCatalog, ConnectorSpecification, Status
from airbyte_cdk.models.airbyte_protocol import DestinationSyncMode
from destination_snowflake_cortex.config import ConfigModel
from destination_snowflake_cortex.indexer import SnowflakeCortexIndexer

BATCH_SIZE = 150


class DestinationSnowflakeCortex(Destination):
    indexer: Indexer
    embedder: Embedder

    def _init_indexer(self, config: ConfigModel, configured_catalog: Optional[ConfiguredAirbyteCatalog] = None):
        self.embedder = create_from_config(config.embedding, config.processing)
        self.indexer = SnowflakeCortexIndexer(config.indexing, self.embedder.embedding_dimensions, configured_catalog)

    def write(
        self, config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog, input_messages: Iterable[AirbyteMessage]
    ) -> Iterable[AirbyteMessage]:
        parsed_config = ConfigModel.parse_obj(config)
        self._init_indexer(parsed_config, configured_catalog)
        writer = Writer(
            parsed_config.processing, self.indexer, self.embedder, batch_size=BATCH_SIZE, omit_raw_text=parsed_config.omit_raw_text
        )
        yield from writer.write(configured_catalog, input_messages)

    def check(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        try:
            parsed_config = ConfigModel.parse_obj(config)
            self._init_indexer(parsed_config)
            self.indexer.check()
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(e)}")

    def spec(self, *args: Any, **kwargs: Any) -> ConnectorSpecification:
        return ConnectorSpecification(
            documentationUrl="https://docs.airbyte.com/integrations/destinations/snowflake-cortex",
            supportsIncremental=True,
            supported_destination_sync_modes=[DestinationSyncMode.overwrite, DestinationSyncMode.append, DestinationSyncMode.append_dedup],
            connectionSpecification=ConfigModel.schema(),  # type: ignore[attr-defined]
        )
