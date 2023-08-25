#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
import dpath.util
import re
from typing import Any, Iterable, List, Literal, Mapping, Optional, Union

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.destinations import Destination
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
from airbyte_cdk.destinations.vector_db_based.batcher import Batcher
from airbyte_cdk.destinations.vector_db_based.config import (
    CohereEmbeddingConfigModel,
    FakeEmbeddingConfigModel,
    OpenAIEmbeddingConfigModel,
    ProcessingConfigModel,
)
from airbyte_cdk.destinations.vector_db_based.document_processor import Chunk, DocumentProcessor
from airbyte_cdk.destinations.vector_db_based.embedder import Embedder, FakeEmbedder, OpenAIEmbedder, CohereEmbedder
from airbyte_cdk.destinations.vector_db_based.indexer import Indexer
from airbyte_cdk.destinations.vector_db_based.utils import format_exception
from jsonschema import RefResolver
from pydantic import BaseModel, Field
from pymilvus import MilvusClient
from pymilvus.exceptions import DescribeCollectionException


BATCH_SIZE = 128


class UsernamePasswordAuth(BaseModel):
    mode: Literal["username_password"] = Field("username_password", const=True)
    username: str = Field(..., title="Username", description="Username for the Milvus instance")
    password: str = Field(..., title="Password", description="Password for the Milvus instance", airbyte_secret=True)


class TokenAuth(BaseModel):
    mode: Literal["token"] = Field("token", const=True)
    token: str = Field(..., title="API Token", description="API Token for the Milvus instance", airbyte_secret=True)


class MilvusIndexingConfigModel(BaseModel):
    host: str = Field(..., title="Public Endpoint")
    db: Optional[str] = Field(title="Database Name", description="The database to connect to", default="")
    collection: str = Field(..., title="Collection Name", description="The collection to load data into")
    auth: Union[UsernamePasswordAuth, TokenAuth] = Field(
        ..., title="Authentication", description="Authentication method", discriminator="mode", type="object"
    )

    class Config:
        title = "Indexing"
        schema_extra =  {
            "group": "Indexing",
            "description": "Indexing configuration",
        }


class ConfigModel(BaseModel):
    processing: ProcessingConfigModel
    embedding: Union[OpenAIEmbeddingConfigModel, CohereEmbeddingConfigModel, FakeEmbeddingConfigModel] = Field(
        ..., title="Embedding", description="Embedding configuration", discriminator="mode", group="embedding", type="object"
    )
    indexing: MilvusIndexingConfigModel

    class Config:
        title = "Milvus Destination Config"
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


class MilvusIndexer(Indexer):
    config: MilvusIndexingConfigModel

    def __init__(self, config: MilvusIndexingConfigModel, embedder: Embedder):
        super().__init__(config, embedder)

    def _create_client(self):
        self._client = MilvusClient(
            uri=self.config.host,
            db=self.config.db if self.config.db else "",
            user=self.config.auth.username if self.config.auth.mode == "username_password" else "",
            password=self.config.auth.password if self.config.auth.mode == "username_password" else "",
            token=self.config.auth.token if self.config.auth.mode == "token" else "",
        )

    def check(self) -> Optional[str]:
        try:
            self._create_client()
            self._client.describe_collection(self.config.collection)
        except DescribeCollectionException as e:
            return f"Collection {self.config.collection} does not exist"
        except Exception as e:
            return format_exception(e)
        return None
    
    def index(self, document_chunks: List[Chunk], delete_ids: List[str]) -> None:
        pass


embedder_map = {"openai": OpenAIEmbedder, "cohere": CohereEmbedder, "fake": FakeEmbedder}


class DestinationMilvus(Destination):
    indexer: Indexer
    processor: DocumentProcessor
    embedder: Embedder

    def _init_indexer(self, config: ConfigModel):
        self.embedder = embedder_map[config.embedding.mode](config.embedding)
        self.indexer = MilvusIndexer(config.indexing, self.embedder)

    def write(
        self, config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog, input_messages: Iterable[AirbyteMessage]
    ) -> Iterable[AirbyteMessage]:
        pass

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
            documentationUrl="https://docs.airbyte.com/integrations/destinations/milvus",
            supportsIncremental=True,
            supported_destination_sync_modes=[DestinationSyncMode.overwrite, DestinationSyncMode.append, DestinationSyncMode.append_dedup],
            connectionSpecification=ConfigModel.schema(),  # type: ignore[attr-defined]
        )
