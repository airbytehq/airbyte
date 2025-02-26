#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Any, Dict, Literal, Optional, Union

import dpath.util
from pydantic.v1 import BaseModel, Field

from airbyte_cdk.sources.file_based.config.abstract_file_based_spec import AbstractFileBasedSpec, DeliverRawFiles, DeliverRecords


class OAuthCredentials(BaseModel):
    """
    OAuthCredentials class to hold authentication details for Microsoft OAuth authentication.
    This class uses pydantic for data validation and settings management.
    """

    class Config:
        title = "Authenticate via Microsoft (OAuth)"

    # Fields for the OAuth authentication, including tenant_id, client_id, client_secret, and refresh_token
    auth_type: Literal["Client"] = Field("Client", const=True)
    tenant_id: str = Field(title="Tenant ID", description="Tenant ID of the Microsoft SharePoint user", airbyte_secret=True)
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
    refresh_token: Optional[str] = Field(
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
    tenant_id: str = Field(title="Tenant ID", description="Tenant ID of the Microsoft SharePoint user", airbyte_secret=True)
    user_principal_name: str = Field(
        title="User Principal Name",
        description="Special characters such as a period, comma, space, and the at sign (@) are converted to underscores (_). More details: https://learn.microsoft.com/en-us/sharepoint/list-onedrive-urls",
        airbyte_secret=True,
    )
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


class SourceMicrosoftSharePointSpec(AbstractFileBasedSpec, BaseModel):
    """
    SourceMicrosoftSharePointSpec class for Microsoft SharePoint Source Specification.
    This class combines the authentication details with additional configuration for the SharePoint API.
    """

    class Config:
        title = "Microsoft SharePoint Source Spec"

    # Union type for credentials, allowing for either OAuth or Service Key authentication
    credentials: Union[OAuthCredentials, ServiceCredentials] = Field(
        title="Authentication",
        description="Credentials for connecting to the One Drive API",
        discriminator="auth_type",
        type="object",
        order=0,
    )

    delivery_method: DeliverRecords | DeliverRawFiles = Field(
        title="Delivery Method",
        discriminator="delivery_type",
        type="object",
        order=1,
        display_type="radio",
        group="advanced",
        default="use_records_transfer",
    )

    search_scope: str = Field(
        title="Search Scope",
        description="Specifies the location(s) to search for files. Valid options are 'ACCESSIBLE_DRIVES' for all SharePoint drives the user can access, 'SHARED_ITEMS' for shared items the user has access to, and 'ALL' to search both.",
        default="ALL",
        enum=["ACCESSIBLE_DRIVES", "SHARED_ITEMS", "ALL"],
        order=3,
    )

    folder_path: str = Field(
        title="Folder Path",
        description="Path to a specific folder within the drives to search for files. Leave empty to search all folders of the drives. This does not apply to shared items.",
        order=4,
        default=".",
    )

    @classmethod
    def documentation_url(cls) -> str:
        """Provides the URL to the documentation for this specific source."""
        return "https://docs.airbyte.com/integrations/sources/microsoft-sharepoint"

    @classmethod
    def schema(cls, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Generates the schema mapping for configuration fields.
        It also cleans up the schema by removing legacy settings and discriminators.
        """
        schema = super().schema(*args, **kwargs)

        # Remove legacy settings related to streams
        dpath.util.delete(schema, "properties/streams/items/properties/legacy_prefix")
        dpath.util.delete(schema, "properties/streams/items/properties/format/oneOf/*/properties/inference_type")

        # Hide API processing option until https://github.com/airbytehq/airbyte-platform-internal/issues/10354 is fixed
        processing_options = dpath.util.get(schema, "properties/streams/items/properties/format/oneOf/4/properties/processing/oneOf")
        dpath.util.set(schema, "properties/streams/items/properties/format/oneOf/4/properties/processing/oneOf", processing_options[:1])

        return schema
