#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
import re
from typing import Literal, Union

import dpath.util
from airbyte_cdk.destinations.vector_db_based.config import (
    AzureOpenAIEmbeddingConfigModel,
    CohereEmbeddingConfigModel,
    FakeEmbeddingConfigModel,
    FromFieldEmbeddingConfigModel,
    OpenAICompatibleEmbeddingConfigModel,
    OpenAIEmbeddingConfigModel,
    ProcessingConfigModel,
)
from jsonschema import RefResolver
from pydantic import BaseModel, Field


class NoAuth(BaseModel):
    mode: Literal["no_auth"] = Field("no_auth", const=True)


class ApiKeyAuth(BaseModel):
    mode: Literal["api_key_auth"] = Field("api_key_auth", const=True)
    api_key: str = Field(..., title="API Key", description="API Key for the Qdrant instance", airbyte_secret=True)


class QdrantIndexingConfigModel(BaseModel):
    url: str = Field(..., title="Public Endpoint", description="Public Endpoint of the Qdrant cluser", order=0)
    auth_method: Union[ApiKeyAuth, NoAuth] = Field(
        default="api_key_auth",
        title="Authentication Method",
        description="Method to authenticate with the Qdrant Instance",
        discriminator="mode",
        type="object",
        order=1,
    )
    prefer_grpc: bool = Field(
        title="Prefer gRPC", description="Whether to prefer gRPC over HTTP. Set to true for Qdrant cloud clusters", default=True
    )
    collection: str = Field(..., title="Collection Name", description="The collection to load data into", order=2)
    distance_metric: Union[Literal["dot"], Literal["cos"], Literal["euc"]] = Field(
        default="cos",
        title="Distance Metric",
        enum=["dot", "cos", "euc"],
        description="The Distance metric used to measure similarities among vectors. This field is only used if the collection defined in the does not exist yet and is created automatically by the connector.",
    )
    text_field: str = Field(title="Text Field", description="The field in the payload that contains the embedded text", default="text")

    class Config:
        title = "Indexing"
        schema_extra = {
            "group": "Indexing",
            "description": "Indexing configuration",
        }


class ConfigModel(BaseModel):
    processing: ProcessingConfigModel
    embedding: Union[
        OpenAIEmbeddingConfigModel,
        CohereEmbeddingConfigModel,
        FakeEmbeddingConfigModel,
        FromFieldEmbeddingConfigModel,
        AzureOpenAIEmbeddingConfigModel,
        OpenAICompatibleEmbeddingConfigModel,
    ] = Field(..., title="Embedding", description="Embedding configuration", discriminator="mode", group="embedding", type="object")
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
        dpath.util.delete(schema, "properties/**/discriminator")

    @classmethod
    def schema(cls):
        """we're overriding the schema classmethod to enable some post-processing"""
        schema = super().schema()
        schema = cls.resolve_refs(schema)
        cls.remove_discriminator(schema)
        return schema
