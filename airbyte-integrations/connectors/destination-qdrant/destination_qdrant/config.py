#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Literal, Union

from pydantic.v1 import BaseModel, Field

from airbyte_cdk.destinations.vector_db_based.config import VectorDBConfigModel


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
    distance_metric: str = Field(
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


class ConfigModel(VectorDBConfigModel):
    indexing: QdrantIndexingConfigModel
