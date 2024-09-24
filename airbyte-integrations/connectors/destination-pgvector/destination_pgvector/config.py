#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


from airbyte_cdk.destinations.vector_db_based.config import VectorDBConfigModel
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


class PGVectorIndexingModel(BaseModel):

    host: str = Field(
        ...,
        title="Host",
        order=1,
        description="Enter the account name you want to use to access the database.",
        examples=["AIRBYTE_ACCOUNT"],
    )
    port: int = Field(
        default=5432,
        title="Port",
        order=2,
        description="Enter the port you want to use to access the database",
        examples=["5432"],
    )
    database: str = Field(
        ...,
        title="Database",
        order=4,
        description="Enter the name of the database that you want to sync data into",
        examples=["AIRBYTE_DATABASE"],
    )
    default_schema: str = Field(
        default="public",
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

    # E.g. "credentials": {"password": "AIRBYTE_PASSWORD"}
    credentials: PasswordBasedAuthorizationModel

    class Config:
        title = "Postgres Connection"
        schema_extra = {
            "description": "Postgres can be used to store vector data and retrieve embeddings.",
            "group": "indexing",
        }


class ConfigModel(VectorDBConfigModel):
    indexing: PGVectorIndexingModel
