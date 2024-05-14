#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


from airbyte_cdk.destinations.vector_db_based.config import VectorDBConfigModel
from pydantic import BaseModel, Field

# to-do - https://github.com/airbytehq/airbyte/issues/38007 - add Snowflake supported models to config

# "indexing": {
#     "host": "NXA17679",
#     "role": "ACCOUNTADMIN",
#     "warehouse": "COMPUTE_WH",
#     "database": "PYAIRBYTE_INTEGRATION_TEST",
#     "schema": "airbyte_raw",
#     "username": "airbytepartneradmin",
#     "credentials": {
#         "password": "t^$JK9g6CfqDH@4U"
#     }
# }


class SnowflakeCortexIndexingModel(BaseModel):
    host: str = Field(
        ...,
        title="Host",
        airbyte_secret=True,
        description="Enter the account name you want to use to access the database. This is usually the identifier before .snowflakecomputing.com",
        examples=["AIRBYTE_ACCOUNT"],
    )
    role: str = Field(
        ...,
        title="Role",
        airbyte_secret=True,
        description="Enter the role that you want to use to access Snowflake",
        examples=["AIRBYTE_ROLE", "ACCOUNTADMIN"],
    )
    warehouse: str = Field(
        ...,
        title="Warehouse",
        airbyte_secret=True,
        description="Enter the name of the warehouse that you want to sync data into",
        examples=["AIRBYTE_WAREHOUSE"],
    )
    database: str = Field(
        ...,
        title="Database",
        airbyte_secret=True,
        description="Enter the name of the database that you want to sync data into",
        examples=["AIRBYTE_DATABASE"],
    )
    default_schema: str = Field(
        ...,
        title="Default Schema",
        airbyte_secret=True,
        description="Enter the name of the default schema",
        examples=["AIRBYTE_SCHEMA"],
    )
    username: str = Field(
        ...,
        title="Username",
        airbyte_secret=True,
        description="Enter the name of the user you want to use to access the database",
        examples=["AIRBYTE_USER"],
    )

    # add a dropdown for password

    password: str = Field(
        ..., title="Password", airbyte_secret=True, description="Enter the password associated with the user you entered above"
    )

    class Config:
        title = "Indexing"
        schema_extra = {
            "description": "Snowflake can be used to store vector data and retrieve embeddings.",
            "group": "indexing",
        }


class ConfigModel(VectorDBConfigModel):
    indexing: SnowflakeCortexIndexingModel
