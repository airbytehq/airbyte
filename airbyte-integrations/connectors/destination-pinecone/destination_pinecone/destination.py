#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Any, Iterable, Mapping

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.destinations import Destination
from airbyte_cdk.destinations.vector_db_based.embedder import AzureOpenAIEmbedder, CohereEmbedder, Embedder, FakeEmbedder, OpenAIEmbedder
from airbyte_cdk.destinations.vector_db_based.indexer import Indexer
from airbyte_cdk.destinations.vector_db_based.writer import Writer
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, ConfiguredAirbyteCatalog, ConnectorSpecification, Status
from airbyte_cdk.models.airbyte_protocol import DestinationSyncMode
from destination_pinecone.config import ConfigModel
from destination_pinecone.indexer import PineconeIndexer

BATCH_SIZE = 32


embedder_map = {"openai": OpenAIEmbedder, "cohere": CohereEmbedder, "fake": FakeEmbedder, "azure_openai": AzureOpenAIEmbedder}


class DestinationPinecone(Destination):
    indexer: Indexer
    embedder: Embedder

    def _init_indexer(self, config: ConfigModel):
        if config.embedding.mode == "azure_openai" or config.embedding.mode == "openai":
            self.embedder = embedder_map[config.embedding.mode](config.embedding, config.processing.chunk_size)
        else:
            self.embedder = embedder_map[config.embedding.mode](config.embedding)
        self.indexer = PineconeIndexer(config.indexing, self.embedder.embedding_dimensions)

    def write(
        self, config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog, input_messages: Iterable[AirbyteMessage]
    ) -> Iterable[AirbyteMessage]:
        config_model = ConfigModel.parse_obj(config)
        self._init_indexer(config_model)
        writer = Writer(config_model.processing, self.indexer, self.embedder, batch_size=BATCH_SIZE)
        yield from writer.write(configured_catalog, input_messages)

    def check(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        self._init_indexer(ConfigModel.parse_obj(config))
        embedder_error = self.embedder.check()
        indexer_error = self.indexer.check()
        errors = [error for error in [embedder_error, indexer_error] if error is not None]
        if len(errors) > 0:
            return AirbyteConnectionStatus(status=Status.FAILED, message="\n".join(errors))
        else:
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)

    def spec(self, *args: Any, **kwargs: Any) -> ConnectorSpecification:
        return ConnectorSpecification(
            documentationUrl="https://docs.airbyte.com/integrations/destinations/pinecone",
            supportsIncremental=True,
            supported_destination_sync_modes=[DestinationSyncMode.overwrite, DestinationSyncMode.append, DestinationSyncMode.append_dedup],
            connectionSpecification=ConfigModel.schema(),  # type: ignore[attr-defined]
        )
