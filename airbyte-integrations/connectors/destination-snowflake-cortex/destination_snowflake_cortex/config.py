#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


from typing import Literal, Union

from airbyte_cdk.destinations.vector_db_based.config import VectorDBConfigModel
from airbyte_cdk.utils.oneof_option_config import OneOfOptionConfig
from pydantic import BaseModel, Field


class PasswordBasedAuthorizationModel(BaseModel):
    password: str = Field(
        ...,
        title="Password",
        airbyte_secret=True,
        description="Enter the password you want to use to access the database",
        examples=["AIRBYTE_PASSWORD"],
        order=7,
    )

    class Config:
        title = "Credentials"


# to-do - https://github.com/airbytehq/airbyte/issues/38007 - add Snowflake supported models to embedding options
class SnowflakeCortexIndexingModel(BaseModel):
    host: str = Field(
        ...,
        title="Host",
        order=1,
        description="Enter the account name you want to use to access the database. This is usually the identifier before .snowflakecomputing.com",
        examples=["AIRBYTE_ACCOUNT"],
    )
    role: str = Field(
        ...,
        title="Role",
        order=2,
        description="Enter the role that you want to use to access Snowflake",
        examples=["AIRBYTE_ROLE", "ACCOUNTADMIN"],
    )
    warehouse: str = Field(
        ...,
        title="Warehouse",
        order=3,
        description="Enter the name of the warehouse that you want to sync data into",
        examples=["AIRBYTE_WAREHOUSE"],
    )
    database: str = Field(
        ...,
        title="Database",
        order=4,
        description="Enter the name of the database that you want to sync data into",
        examples=["AIRBYTE_DATABASE"],
    )
    default_schema: str = Field(
        ...,
        title="Default Schema",
        order=5,
        description="Enter the name of the default schema",
        examples=["AIRBYTE_SCHEMA"],
    )
    username: str = Field(
        ...,
        title="Username",
        order=6,
        description="Enter the name of the user you want to use to access the database",
        examples=["AIRBYTE_USER"],
    )

    credentials: PasswordBasedAuthorizationModel

    class Config:
        title = "Indexing"
        schema_extra = {
            "description": "Snowflake can be used to store vector data and retrieve embeddings.",
            "group": "indexing",
        }


class ConfigModel(VectorDBConfigModel):
    indexing: SnowflakeCortexIndexingModel
