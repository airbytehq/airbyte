#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Any, Dict, Literal, Union

import dpath.util
from airbyte_cdk.sources.file_based.config.abstract_file_based_spec import AbstractFileBasedSpec
from pydantic import BaseModel, Field


class OAuthCredentials(BaseModel):
    """
    OAuthCredentials class to hold authentication details for Microsoft OAuth authentication.
    This class uses pydantic for data validation and settings management.
    """

    class Config:
        title = "Authenticate via Microsoft (OAuth)"

    # Fields for the OAuth authentication, including tenant_id, client_id, client_secret, and refresh_token
    auth_type: Literal["Client"] = Field("Client", const=True)
    tenant_id: str = Field(title="Tenant ID", description="Tenant ID of the Microsoft OneDrive user")
    client_id: str = Field(
        title="Client ID",
        description="Client ID of your Microsoft developer application",
        airbyte_secret=True,
    )
    client_secret: str = Field(
        title="Client Secret",
        description="Client Secret of your Microsoft developer application",
        airbyte_secret=True,
    )
    refresh_token: str = Field(
        title="Refresh Token",
        description="Refresh Token of your Microsoft developer application",
        airbyte_secret=True,
    )


class ServiceCredentials(BaseModel):
    """
    ServiceCredentials class for service key authentication.
    This class is structured similarly to OAuthCredentials but for a different authentication method.
    """

    class Config:
        title = "Service Key Authentication"

    # Fields for the Service authentication, similar to OAuthCredentials
    auth_type: Literal["Service"] = Field("Service", const=True)
    tenant_id: str = Field(title="Tenant ID", description="Tenant ID of the Microsoft OneDrive user")
    client_id: str = Field(
        title="Client ID",
        description="Client ID of your Microsoft developer application",
        airbyte_secret=True,
    )
    client_secret: str = Field(
        title="Client Secret",
        description="Client Secret of your Microsoft developer application",
        airbyte_secret=True,
    )


# TODO: Add filtration by folder name in stream config
class SourceMicrosoftOneDriveSpec(AbstractFileBasedSpec, BaseModel):
    """
    SourceMicrosoftOneDriveSpec class for Microsoft OneDrive Source Specification.
    This class combines the authentication details with additional configuration for the OneDrive API.
    """

    class Config:
        title = "Microsoft OneDrive Source Spec"

    # Union type for credentials, allowing for either OAuth or Service Key authentication
    credentials: Union[OAuthCredentials, ServiceCredentials] = Field(
        title="Authentication",
        description="Credentials for connecting to the One Drive API",
        discriminator="auth_type",
        type="object",
        order=0,
    )

    drive_name: str = Field(title="Drive Name", description="Name of the Microsoft OneDrive drive where the file(s) exist.", order=1)

    @classmethod
    def documentation_url(cls) -> str:
        """Provides the URL to the documentation for this specific source."""
        return "https://docs.airbyte.com/integrations/sources/one-drive"

    @staticmethod
    def remove_discriminator(schema: dict) -> None:
        """
        Removes the discriminator field added by pydantic in oneOf schemas.
        This is necessary for correct treatment by the platform.
        """
        dpath.util.delete(schema, "properties/*/discriminator")

    @classmethod
    def schema(cls, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Generates the schema mapping for configuration fields.
        It also cleans up the schema by removing legacy settings and discriminators.
        """
        schema = super().schema(*args, **kwargs)
        cls.remove_discriminator(schema)

        # Remove legacy settings related to streams
        dpath.util.delete(schema, "properties/streams/items/properties/legacy_prefix")
        dpath.util.delete(schema, "properties/streams/items/properties/format/oneOf/*/properties/inference_type")

        return schema
