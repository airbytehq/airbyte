#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import dpath.util
import json
import re

from jsonschema import RefResolver
from typing import Literal, Union

from airbyte_cdk.destinations.vector_db_based.config import (
    CohereEmbeddingConfigModel,
    FakeEmbeddingConfigModel,
    FromFieldEmbeddingConfigModel,
    OpenAIEmbeddingConfigModel,
    ProcessingConfigModel,
)
from pydantic import BaseModel, Field



class LocalServerAuth(BaseModel):
    mode: Literal["local_server"] = Field("local_server", const=True)
    host: str = Field(..., title="Host", description="Host of the Qdrant instance")
    port: str = Field(..., title="Port", description="Port of the Qdrant instance")
    grpc_port: str = Field(..., title="gRPC Port", description="gRPC Port of the Qdrant instance", default="")

class CloudAuth(BaseModel):
    mode: Literal["cloud"] = Field("cloud", const=True)
    url: str = Field(..., title="url", description="url of the Qdrant instance")
    api_key: str = Field(..., title="API Key", description="API Key for the Qdrant instance", airbyte_secret=True)


class QdrantIndexingConfigModel(BaseModel):
    auth_method: Union[LocalServerAuth, CloudAuth] = Field(
        ..., title="Authentication Method", description="Method to connect to the Qdrant Instance", discriminator="mode", type="object", order=0
    )
    prefer_grpc: bool = Field(
        title="Prefer gRPC", description="Whether to prefer gRPC over HTTP. Set to true for Qdrant cloud clusters", default=True
    )
    collection: str = Field(..., title="Collection Name", description="The collection to load data into")
    # text_field: str = Field(title="Text Field", description="The field in the entity that contains the embedded text", default="text")

    class Config:
        title = "Indexing"
        schema_extra = {
            "group": "Indexing",
            "description": "Indexing configuration",
        }


class ConfigModel(BaseModel):
    processing: ProcessingConfigModel
    embedding: Union[OpenAIEmbeddingConfigModel, CohereEmbeddingConfigModel, FakeEmbeddingConfigModel, FromFieldEmbeddingConfigModel] = Field(
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
