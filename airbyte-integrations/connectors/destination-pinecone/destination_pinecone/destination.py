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
from airbyte_protocol.models.airbyte_protocol import AirbyteLogMessage, Level
from destination_pinecone.config import ConfigModel
from destination_pinecone.indexer import PineconeIndexer


BATCH_SIZE = 32


class DestinationPinecone(Destination):
    indexer: Indexer
    embedder: Embedder

    def _init_indexer(self, config: ConfigModel):
        try:
            self.embedder = create_from_config(config.embedding, config.processing)
            self.indexer = PineconeIndexer(config.indexing, self.embedder.embedding_dimensions)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=str(e))

    def write(
        self, config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog, input_messages: Iterable[AirbyteMessage]
    ) -> Iterable[AirbyteMessage]:
        try:
            config_model = ConfigModel.parse_obj(config)
            self._init_indexer(config_model)
            writer = Writer(
                config_model.processing, self.indexer, self.embedder, batch_size=BATCH_SIZE, omit_raw_text=config_model.omit_raw_text
            )
            yield from writer.write(configured_catalog, input_messages)
        except Exception as e:
            log_message = AirbyteLogMessage(level=Level.ERROR, message=str(e))
            yield AirbyteMessage(type="LOG", message=log_message)

    def check(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        try:
            parsed_config = ConfigModel.parse_obj(config)
            init_status = self._init_indexer(parsed_config)
            if init_status and init_status.status == Status.FAILED:
                logger.error(f"Initialization failed with message: {init_status.message}")
                return init_status  # Return the failure status immediately if initialization fails

            checks = [self.embedder.check(), self.indexer.check(), DocumentProcessor.check_config(parsed_config.processing)]
            errors = [error for error in checks if error is not None]
            if len(errors) > 0:
                error_message = "\n".join(errors)
                logger.error(f"Configuration check failed: {error_message}")
                return AirbyteConnectionStatus(status=Status.FAILED, message=error_message)
            else:
                return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            logger.error(f"Exception during configuration check: {str(e)}")
            return AirbyteConnectionStatus(status=Status.FAILED, message=str(e))

    def spec(self, *args: Any, **kwargs: Any) -> ConnectorSpecification:
        return ConnectorSpecification(
            documentationUrl="https://docs.airbyte.com/integrations/destinations/pinecone",
            supportsIncremental=True,
            supported_destination_sync_modes=[DestinationSyncMode.overwrite, DestinationSyncMode.append, DestinationSyncMode.append_dedup],
            connectionSpecification=ConfigModel.schema(),  # type: ignore[attr-defined]
        )
