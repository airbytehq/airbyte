#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
from typing import Any, Iterable, Mapping

from airbyte_cdk.destinations import Destination
from airbyte_cdk.destinations.vector_db_based.document_processor import DocumentProcessor
from airbyte_cdk.destinations.vector_db_based.embedder import Embedder, create_from_config
from airbyte_cdk.destinations.vector_db_based.indexer import Indexer
from airbyte_cdk.destinations.vector_db_based.writer import Writer
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, ConfiguredAirbyteCatalog, ConnectorSpecification, Status
from airbyte_cdk.models.airbyte_protocol import DestinationSyncMode
from destination_astra.config import ConfigModel
from destination_astra.indexer import AstraIndexer

BATCH_SIZE = 100


class DestinationAstra(Destination):
    indexer: Indexer
    embedder: Embedder

    def _init_indexer(self, config: ConfigModel):
        self.embedder = create_from_config(config.embedding, config.processing)
        self.indexer = AstraIndexer(config.indexing, self.embedder.embedding_dimensions)

    def write(
        self, config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog, input_messages: Iterable[AirbyteMessage]
    ) -> Iterable[AirbyteMessage]:
        config_model = ConfigModel.parse_obj(config)
        self._init_indexer(config_model)
        writer = Writer(
            config_model.processing, self.indexer, self.embedder, batch_size=BATCH_SIZE, omit_raw_text=config_model.omit_raw_text
        )
        yield from writer.write(configured_catalog, input_messages)

    def check(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        parsed_config = ConfigModel.parse_obj(config)
        self._init_indexer(parsed_config)
        checks = [self.embedder.check(), self.indexer.check(), DocumentProcessor.check_config(parsed_config.processing)]
        errors = [error for error in checks if error is not None]
        if len(errors) > 0:
            return AirbyteConnectionStatus(status=Status.FAILED, message="\n".join(errors))
        else:
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)

    def spec(self, *args: Any, **kwargs: Any) -> ConnectorSpecification:
        return ConnectorSpecification(
            documentationUrl="https://docs.airbyte.com/integrations/destinations/astra",
            supportsIncremental=True,
            supported_destination_sync_modes=[DestinationSyncMode.overwrite, DestinationSyncMode.append, DestinationSyncMode.append_dedup],
            connectionSpecification=ConfigModel.schema(),  # type: ignore[attr-defined]
        )
