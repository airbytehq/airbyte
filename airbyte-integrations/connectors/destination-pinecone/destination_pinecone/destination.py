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

    def _log(self, level: Level, message: str) -> AirbyteMessage:
        return AirbyteMessage(type="LOG", log=AirbyteLogMessage(level=level, message=message))

    def write(
        self, config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog, input_messages: Iterable[AirbyteMessage]
    ) -> Iterable[AirbyteMessage]:
        yield self._log(Level.INFO, "Starting Pinecone destination write...")
        try:
            yield self._log(Level.INFO, "Parsing configuration...")
            config_model = ConfigModel.parse_obj(config)

            yield self._log(Level.INFO, "Initializing embedder and indexer...")
            self._init_indexer(config_model)

            yield self._log(Level.INFO, "Creating writer and starting sync...")
            writer = Writer(
                config_model.processing, self.indexer, self.embedder, batch_size=BATCH_SIZE, omit_raw_text=config_model.omit_raw_text
            )
            yield from writer.write(configured_catalog, input_messages)
            yield self._log(Level.INFO, "Write operation completed.")
        except Exception as e:
            yield self._log(Level.ERROR, f"Exception during write: {str(e)}")

    def check(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        logger.info("Starting Pinecone destination check...")
        try:
            logger.info("Parsing configuration...")
            parsed_config = ConfigModel.parse_obj(config)

            logger.info("Initializing embedder and indexer...")
            init_status = self._init_indexer(parsed_config)
            if init_status and init_status.status == Status.FAILED:
                logger.error(f"Initialization failed with message: {init_status.message}")
                return init_status

            logger.info("Running embedder check...")
            embedder_check_result = self.embedder.check()

            logger.info("Running indexer check...")
            indexer_check_result = self.indexer.check()

            logger.info("Running document processor config check...")
            processor_check_result = DocumentProcessor.check_config(parsed_config.processing)

            checks = [embedder_check_result, indexer_check_result, processor_check_result]
            errors = [error for error in checks if error is not None]
            if len(errors) > 0:
                error_message = "\n".join(errors)
                logger.error(f"Configuration check failed: {error_message}")
                return AirbyteConnectionStatus(status=Status.FAILED, message=error_message)
            else:
                logger.info("Configuration check succeeded.")
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
