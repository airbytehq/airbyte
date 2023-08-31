#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
import re
import uuid
from typing import Any, Iterable, List, Literal, Mapping, Optional, Union

import dpath.util
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.destinations import Destination
from airbyte_cdk.destinations.vector_db_based.batcher import Batcher
from airbyte_cdk.destinations.vector_db_based.config import (
    CohereEmbeddingConfigModel,
    FakeEmbeddingConfigModel,
    OpenAIEmbeddingConfigModel,
    ProcessingConfigModel,
)
from airbyte_cdk.destinations.vector_db_based.document_processor import (
    METADATA_RECORD_ID_FIELD,
    METADATA_STREAM_FIELD,
    Chunk,
    DocumentProcessor,
)
from airbyte_cdk.destinations.vector_db_based.embedder import CohereEmbedder, Embedder, FakeEmbedder, OpenAIEmbedder
from airbyte_cdk.destinations.vector_db_based.indexer import Indexer
from airbyte_cdk.destinations.vector_db_based.utils import format_exception
from airbyte_cdk.destinations.vector_db_based.writer import Writer
from airbyte_cdk.models import (
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    ConfiguredAirbyteCatalog,
    ConnectorSpecification,
    Status,
    Type,
)
from airbyte_cdk.models.airbyte_protocol import DestinationSyncMode
from jsonschema import RefResolver
from pydantic import BaseModel, Field
from qdrant_client import QdrantClient, models
from qdrant_client.conversions.common_types import PointsSelector

BATCH_SIZE = 256


class UsernamePasswordAuth(BaseModel):
    mode: Literal["username_password"] = Field("username_password", const=True)
    username: str = Field(..., title="Username", description="Username for the Qdrant instance")
    password: str = Field(..., title="Password", description="Password for the Qdrant instance", airbyte_secret=True)


class TokenAuth(BaseModel):
    mode: Literal["token"] = Field("token", const=True)


class QdrantIndexingConfigModel(BaseModel):
    host: str = Field(..., title="Public Endpoint")
    token: str = Field(..., title="API Token", description="API Token for the Qdrant instance", airbyte_secret=True)
    prefer_grpc: bool = Field(
        title="Prefer gRPC", description="Whether to prefer gRPC over HTTP. Set to true for Qdrant cloud clusters", default=True
    )
    collection: str = Field(..., title="Collection Name", description="The collection to load data into")
    text_field: str = Field(title="Text Field", description="The field in the entity that contains the embedded text", default="text")

    class Config:
        title = "Indexing"
        schema_extra = {
            "group": "Indexing",
            "description": "Indexing configuration",
        }


class ConfigModel(BaseModel):
    processing: ProcessingConfigModel
    embedding: Union[OpenAIEmbeddingConfigModel, CohereEmbeddingConfigModel, FakeEmbeddingConfigModel] = Field(
        ..., title="Embedding", description="Embedding configuration", discriminator="mode", group="embedding", type="object"
    )
    indexing: QdrantIndexingConfigModel

    class Config:
        title = "Qdrant Destination Config"
        schema_extra = {
            "groups": [
                {"id": "processing", "title": "Processing"},
                {"id": "embedding", "title": "Embedding"},
                {"id": "indexing", "title": "Indexing"},
            ]
        }

    @staticmethod
    def resolve_refs(schema: dict) -> dict:
        # config schemas can't contain references, so inline them
        json_schema_ref_resolver = RefResolver.from_schema(schema)
        str_schema = json.dumps(schema)
        for ref_block in re.findall(r'{"\$ref": "#\/definitions\/.+?(?="})"}', str_schema):
            ref = json.loads(ref_block)["$ref"]
            str_schema = str_schema.replace(ref_block, json.dumps(json_schema_ref_resolver.resolve(ref)[1]))
        pyschema: dict = json.loads(str_schema)
        del pyschema["definitions"]
        return pyschema

    @staticmethod
    def remove_discriminator(schema: dict) -> None:
        """pydantic adds "discriminator" to the schema for oneOfs, which is not treated right by the platform as we inline all references"""
        dpath.util.delete(schema, "properties/*/discriminator")

    @classmethod
    def schema(cls):
        """we're overriding the schema classmethod to enable some post-processing"""
        schema = super().schema()
        schema = cls.resolve_refs(schema)
        cls.remove_discriminator(schema)
        return schema


class QdrantIndexer(Indexer):
    config: QdrantIndexingConfigModel

    def __init__(self, config: QdrantIndexingConfigModel, embedder: Embedder):
        super().__init__(config, embedder)

    def _create_client(self):
        self._client = QdrantClient(self.config.host, prefer_grpc=self.config.prefer_grpc, api_key=self.config.token)

        self._collection = self._client.get_collection(self.config.collection)

    def check(self) -> Optional[str]:
        try:
            self._create_client()
            # TODO - do some checks
        except Exception as e:
            return format_exception(e)
        return None

    def pre_sync(self, catalog: ConfiguredAirbyteCatalog) -> None:
        self._create_client()
        for stream in catalog.streams:
            if stream.destination_sync_mode == DestinationSyncMode.overwrite:
                self._delete_for_filter(
                    models.FilterSelector(
                        filter=models.Filter(
                            must=[models.FieldCondition(key=METADATA_STREAM_FIELD, match=models.MatchValue(value=stream.stream.name))]
                        )
                    )
                )

    def _delete_for_filter(self, selector: PointsSelector) -> None:
        self._client.delete(collection_name=self.config.collection, points_selector=selector)

    def index(self, document_chunks: List[Chunk], delete_ids: List[str]) -> None:
        if len(delete_ids) > 0:
            self._delete_for_filter(
                models.FilterSelector(
                    filter=models.Filter(
                        should=[models.FieldCondition(key=METADATA_RECORD_ID_FIELD, match=models.MatchValue(value=id)) for id in delete_ids]
                    )
                )
            )
        embedding_vectors = self.embedder.embed_texts([chunk.page_content for chunk in document_chunks])
        entities = []
        for i in range(len(document_chunks)):
            chunk = document_chunks[i]
            metadata = chunk.metadata
            metadata["text"] = chunk.page_content
            entities.append(
                models.Record(
                    id=str(uuid.uuid4()),
                    payload={**chunk.metadata, self.config.text_field: chunk.page_content},
                    vector=embedding_vectors[i],
                )
            )
        self._client.upload_records(collection_name=self.config.collection, records=entities)


embedder_map = {"openai": OpenAIEmbedder, "cohere": CohereEmbedder, "fake": FakeEmbedder}


class DestinationQdrant(Destination):
    indexer: Indexer
    processor: DocumentProcessor
    embedder: Embedder

    def _init_indexer(self, config: ConfigModel):
        self.embedder = embedder_map[config.embedding.mode](config.embedding)
        self.indexer = QdrantIndexer(config.indexing, self.embedder)

    def write(
        self, config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog, input_messages: Iterable[AirbyteMessage]
    ) -> Iterable[AirbyteMessage]:
        config_model = ConfigModel.parse_obj(config)
        self._init_indexer(config_model)
        writer = Writer(config_model.processing, self.indexer, batch_size=BATCH_SIZE)
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
            documentationUrl="https://docs.airbyte.com/integrations/destinations/qdrant",
            supportsIncremental=True,
            supported_destination_sync_modes=[DestinationSyncMode.overwrite, DestinationSyncMode.append, DestinationSyncMode.append_dedup],
            connectionSpecification=ConfigModel.schema(),  # type: ignore[attr-defined]
        )
