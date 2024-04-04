#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.destinations.vector_db_based.config import VectorDBConfigModel
from pydantic import BaseModel, Field


class SnowflakeCortexIndexingModel(BaseModel):
    account: str = Field(
        ...,
        title="Account",
        airbyte_secret=True,
        description="Enter the account name you want to use to access the database.",
        examples=["xxx.us-east-2.aws"]
    )
    username: str = Field(
        ..., 
        title="Username", 
        airbyte_secret=True,
        description="Enter the name of the user you want to use to access the database", 
        examples=["AIRBYTE_USER"]
    )
    password: str = Field(
        ..., 
        title="Password", 
        airbyte_secret=True, 
        description="Enter the password associated with the user you entered above"
    )
    database: str = Field(
        ...,
        title="Database",
        airbyte_secret=True,
        description="Enter the name of the database that you want to sync data into",
        examples=["AIRBYTE_DATABASE"]
    )
    warehouse: str = Field(
        ..., 
        title="Warehouse", 
        airbyte_secret=True, 
        description="Enter the name of the warehouse that you want to sync data into", 
        examples=["AIRBYTE_WAREHOUSE"]
    )
    role: str = Field(
        ..., 
        title="Role", 
        airbyte_secret=True, 
        description="Enter the name of the role that you want to sync data into", 
        examples=["AIRBYTE_ROLE", "ACCOUNTADMIN"]
    )

    class Config:
        title = "Indexing"
        schema_extra = {
            "description": "Snowflake cortex comprises database functions tailored for ML and LLM related tasks",
            "group": "indexing",
        }


class ConfigModel(VectorDBConfigModel):
    indexing: SnowflakeCortexIndexingModel
