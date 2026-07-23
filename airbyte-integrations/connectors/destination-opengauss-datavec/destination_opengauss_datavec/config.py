#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from typing import Any, Dict, Literal, Type, Union

from pydantic import BaseModel, Field

from airbyte_cdk.destinations.vector_db_based.config import VectorDBConfigModel


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


class SslModeDisable(BaseModel):
    mode: Literal["disable"] = Field("disable", const=True, order=0)

    class Config:
        title = "disable"
        schema_extra = {"description": "Disable SSL."}


class SslModeAllow(BaseModel):
    mode: Literal["allow"] = Field("allow", const=True, order=0)

    class Config:
        title = "allow"
        schema_extra = {"description": "Allow SSL mode."}


class SslModePrefer(BaseModel):
    mode: Literal["prefer"] = Field("prefer", const=True, order=0)

    class Config:
        title = "prefer"
        schema_extra = {"description": "Prefer SSL mode."}


class SslModeRequire(BaseModel):
    mode: Literal["require"] = Field("require", const=True, order=0)

    class Config:
        title = "require"
        schema_extra = {"description": "Require SSL mode."}


class SslModeVerifyCa(BaseModel):
    mode: Literal["verify-ca"] = Field("verify-ca", const=True, order=0)
    ca_certificate: str = Field(
        ...,
        title="CA Certificate",
        description="CA certificate",
        airbyte_secret=True,
        multiline=True,
        order=1,
    )

    class Config:
        title = "verify-ca"
        schema_extra = {"description": "Verify-ca SSL mode."}


SslMode = Union[SslModeDisable, SslModeAllow, SslModePrefer, SslModeRequire, SslModeVerifyCa]


class OpenGaussDataVecIndexingModel(BaseModel):
    host: str = Field(
        ...,
        title="Host",
        order=1,
        description="Enter the host name or IP address you want to use to access the database.",
        examples=["AIRBYTE_HOST"],
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
    ssl_mode: SslMode = Field(
        default_factory=SslModeDisable,
        title="SSL Modes",
        description=(
            "SSL connection modes.\n"
            "  <b>disable</b> - Disables encryption of communication between Airbyte and destination database.\n"
            "  <b>allow</b> - Enables encryption only when required by the destination database.\n"
            "  <b>prefer</b> - Allows unencrypted connections only if the destination database does not support encryption.\n"
            "  <b>require</b> - Always require encryption. If the destination database server does not support encryption, connection will fail.\n"
            "  <b>verify-ca</b> - Always require encryption and verifies that the destination database server has a valid SSL certificate."
        ),
        order=7,
    )

    credentials: PasswordBasedAuthorizationModel

    class Config:
        title = "openGauss DataVec Connection"

        @staticmethod
        def schema_extra(schema: Dict[str, Any], model: Type["OpenGaussDataVecIndexingModel"]) -> None:
            schema["description"] = "openGauss DataVec can be used to store vector data and retrieve embeddings."
            schema["group"] = "indexing"
            ssl_mode_schema = schema.get("properties", {}).get("ssl_mode", {})
            if "anyOf" in ssl_mode_schema:
                ssl_mode_schema["oneOf"] = ssl_mode_schema.pop("anyOf")
            ssl_mode_schema["type"] = "object"


class ConfigModel(VectorDBConfigModel):
    indexing: OpenGaussDataVecIndexingModel
