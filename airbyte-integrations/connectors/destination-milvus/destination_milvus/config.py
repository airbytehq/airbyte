#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Literal, Optional, Union

from airbyte_cdk.destinations.vector_db_based.config import VectorDBConfigModel
from airbyte_cdk.utils.oneof_option_config import OneOfOptionConfig
from pydantic import BaseModel, Field


class UsernamePasswordAuth(BaseModel):
    mode: Literal["username_password"] = Field("username_password", const=True)
    username: str = Field(..., title="Username", description="Username for the Milvus instance", order=1)
    password: str = Field(..., title="Password", description="Password for the Milvus instance", airbyte_secret=True, order=2)

    class Config(OneOfOptionConfig):
        title = "Username/Password"
        description = "Authenticate using username and password (suitable for self-managed Milvus clusters)"
        discriminator = "mode"


class NoAuth(BaseModel):
    mode: Literal["no_auth"] = Field("no_auth", const=True)

    class Config(OneOfOptionConfig):
        title = "No auth"
        description = "Do not authenticate (suitable for locally running test clusters, do not use for clusters with public IP addresses)"
        discriminator = "mode"


class TokenAuth(BaseModel):
    mode: Literal["token"] = Field("token", const=True)
    token: str = Field(..., title="API Token", description="API Token for the Milvus instance", airbyte_secret=True)

    class Config(OneOfOptionConfig):
        title = "API Token"
        description = "Authenticate using an API token (suitable for Zilliz Cloud)"
        discriminator = "mode"


class MilvusIndexingConfigModel(BaseModel):
    host: str = Field(
        ...,
        title="Public Endpoint",
        order=1,
        description="The public endpoint of the Milvus instance. ",
        examples=["https://my-instance.zone.zillizcloud.com", "tcp://host.docker.internal:19530", "tcp://my-local-milvus:19530"],
    )
    db: Optional[str] = Field(title="Database Name", description="The database to connect to", default="")
    collection: str = Field(..., title="Collection Name", description="The collection to load data into", order=3)
    auth: Union[TokenAuth, UsernamePasswordAuth, NoAuth] = Field(
        ..., title="Authentication", description="Authentication method", discriminator="mode", type="object", order=2
    )
    vector_field: str = Field(title="Vector Field", description="The field in the entity that contains the vector", default="vector")
    text_field: str = Field(title="Text Field", description="The field in the entity that contains the embedded text", default="text")

    class Config:
        title = "Indexing"
        schema_extra = {
            "group": "indexing",
            "description": "Indexing configuration",
        }


class ConfigModel(VectorDBConfigModel):
    indexing: MilvusIndexingConfigModel
