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
from airbyte_cdk.models import (
    AirbyteConnectionStatus,
    AirbyteMessage,
    ConfiguredAirbyteCatalog,
    ConnectorSpecification,
    DestinationSyncMode,
    Status,
)
from destination_chroma.config import ConfigModel
from destination_chroma.indexer import ChromaIndexer
from destination_chroma.no_embedder import NoEmbedder

BATCH_SIZE = 128


class DestinationChroma(Destination):

    indexer: Indexer
    embedder: Embedder

    def _init_indexer(self, config: ConfigModel):
        self.embedder = (
            create_from_config(config.embedding, config.processing)
            if config.embedding.mode != "no_embedding"
            else NoEmbedder(config.embedding)
        )
        self.indexer = ChromaIndexer(config.indexing)

    def write(
        self, config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog, input_messages: Iterable[AirbyteMessage]
    ) -> Iterable[AirbyteMessage]:

        """
        Reads the input stream of messages, config, and catalog to write data to the destination.

        This method returns an iterable (typically a generator of AirbyteMessages via yield) containing state messages received
        in the input message stream. Outputting a state message means that every AirbyteRecordMessage which came before it has been
        successfully persisted to the destination. This is used to ensure fault tolerance in the case that a sync fails before fully completing,
        then the source is given the last state message output from this method as the starting point of the next sync.

        :param config: dict of JSON configuration matching the configuration declared in spec.json
        :param configured_catalog: The Configured Catalog describing the schema of the data being received and how it should be persisted in the
                                    destination
        :param input_messages: The stream of input messages received from the source
        :return: Iterable of AirbyteStateMessages wrapped in AirbyteMessage structs
        """

        config_model = ConfigModel.parse_obj(config)
        self._init_indexer(config_model)
        writer = Writer(
            config_model.processing, self.indexer, self.embedder, batch_size=BATCH_SIZE, omit_raw_text=config_model.omit_raw_text
        )
        yield from writer.write(configured_catalog, input_messages)

    def check(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        """
        Tests if the input configuration can be used to successfully connect to the destination with the needed permissions
            e.g: if a provided API token or password can be used to connect and write to the destination.

        :param logger: Logging object to display debug/info/error to the logs
            (logs will not be accessible via airbyte UI if they are not passed to this logger)
        :param config: Json object containing the configuration of this destination, content of this json is as specified in
        the properties of the spec.json file

        :return: AirbyteConnectionStatus indicating a Success or Failure
        """
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
            documentationUrl="https://docs.airbyte.com/integrations/destinations/chroma",
            supportsIncremental=True,
            supported_destination_sync_modes=[DestinationSyncMode.overwrite, DestinationSyncMode.append, DestinationSyncMode.append_dedup],
            connectionSpecification=ConfigModel.schema(),
        )
