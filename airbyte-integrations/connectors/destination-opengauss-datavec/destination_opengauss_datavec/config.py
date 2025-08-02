#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.destinations.vector_db_based.config import VectorDBConfigModel
from pydantic import BaseModel, Field


class OpenGaussDatavecIndexingModel(BaseModel):
    host: str = Field(
        ...,
        title="Host",
        order=1,
        description="Hostname of the database.",
    )
    database: str = Field(
        ...,
        title="Database",
        order=2,
        description="Enter the name of the database that you want to sync data into",
        examples=["AIRBYTE_DATABASE"],
    )
    username: str = Field(
        ...,
        title="Username",
        order=3,
        description="Enter the name of the user you want to use to access the database",
        examples=["root"],
    )
    password: str = Field(
        ...,
        title="Password",
        order=4,
        description="Enter the password of the user you want to use to access the database",
    )

    port: int = Field(
        default=5432,
        title="Port",
        description="Enter the port you want to use to access the database",
        examples=["5432"],
    )
    default_schema: str = Field(
        default="public",
        title="Default Schema",
        order=6,
        description="Enter the name of the default schema",
        examples=["AIRBYTE_SCHEMA"],
    )


    class Config:
        title = "Indexing"
        schema_extra = {
            "description": "Indexing configuration",
            "group": "indexing",
        }


class ConfigModel(VectorDBConfigModel):
    indexing: OpenGaussDatavecIndexingModel