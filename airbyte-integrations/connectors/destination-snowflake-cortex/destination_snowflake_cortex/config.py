#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


from airbyte_cdk.destinations.vector_db_based.config import VectorDBConfigModel
from pydantic import BaseModel, Field
from typing import Literal, Union


class PasswordBasedAuthorizationModel(BaseModel):
    auth_type: Literal["password"] = Field(
        default="password",
        const=True,
    )
    password: str = Field(
        ...,
        title="Password",
        airbyte_secret=True,
        description="Enter the password you want to use to access the database",
        examples=["AIRBYTE_PASSWORD"],
        order=7,
    )

    class Config:
        title = "Username and Password"


class KeyPairAuthorizationModel(BaseModel):
    auth_type: Literal["key_pair"] = Field(
        default="key_pair",
        const=True,
    )
    private_key: str = Field(
        ...,
        title="Private Key",
        airbyte_secret=True,
        description="RSA Private key to use for key pair authentication. Enter the private key as a string.",
        multiline=True,
    )
    private_key_passphrase: str | None = Field(
        default=None,
        title="Private Key Passphrase",
        airbyte_secret=True,
        description="Passphrase for private key if the key is encrypted. Leave empty if the key is not encrypted.",
    )

    class Config:
        title = "Key Pair Authentication"


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
        description="Enter the name of the warehouse that you want to use as a compute cluster",
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

    credentials: Union[PasswordBasedAuthorizationModel, KeyPairAuthorizationModel] = Field(
        ...,
        title="Authorization Method",
        description="Choose the authorization method for the Snowflake connection",
        discriminator="auth_type",
        type="object",
        oneOf=[
            {"title": "Username and Password", "required": ["password"], "properties": {"auth_type": {"type": "string", "const": "password"}}},
            {"title": "Key Pair Authentication", "required": ["private_key"], "properties": {"auth_type": {"type": "string", "const": "key_pair"}}},
        ],
    )

    class Config:
        title = "Snowflake Connection"
        schema_extra = {
            "description": "Snowflake can be used to store vector data and retrieve embeddings.",
            "group": "indexing",
        }


class ConfigModel(VectorDBConfigModel):
    indexing: SnowflakeCortexIndexingModel
