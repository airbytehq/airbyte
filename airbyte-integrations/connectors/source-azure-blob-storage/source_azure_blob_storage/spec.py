#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Any, Dict, Literal, Optional, Union

import dpath.util
from airbyte_cdk import OneOfOptionConfig
from airbyte_cdk.sources.file_based.config.abstract_file_based_spec import AbstractFileBasedSpec
from pydantic import AnyUrl, BaseModel, Field


class Oauth2(BaseModel):
    class Config(OneOfOptionConfig):
        title = "Authenticate via Oauth2"
        discriminator = "auth_type"

    auth_type: Literal["oauth2"] = Field("oauth2", const=True)
    tenant_id: str = Field(title="Tenant ID", description="Tenant ID of the Microsoft Azure Application user", airbyte_secret=True)
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


class StorageAccountKey(BaseModel):
    class Config(OneOfOptionConfig):
        title = "Authenticate via Storage Account Key"
        discriminator = "auth_type"

    auth_type: Literal["storage_account_key"] = Field("storage_account_key", const=True)
    azure_blob_storage_account_key: str = Field(
        title="Azure Blob Storage account key",
        description="The Azure blob storage account key.",
        airbyte_secret=True,
        examples=["Z8ZkZpteggFx394vm+PJHnGTvdRncaYS+JhLKdj789YNmD+iyGTnG+PV+POiuYNhBg/ACS+LKjd%4FG3FHGN12Nd=="],
        order=3,
    )


class SourceAzureBlobStorageSpec(AbstractFileBasedSpec):
    """
    NOTE: When this Spec is changed, legacy_config_transformer.py must also be modified to uptake the changes
    because it is responsible for converting legacy Azure Blob Storage v0 configs into v1 configs using the File-Based CDK.
    """

    @classmethod
    def documentation_url(cls) -> AnyUrl:
        return AnyUrl("https://docs.airbyte.com/integrations/sources/azure-blob-storage", scheme="https")

    credentials: Union[Oauth2, StorageAccountKey] = Field(
        title="Authentication",
        description="Credentials for connecting to the Azure Blob Storage",
        discriminator="auth_type",
        type="object",
        order=2,
    )
    azure_blob_storage_account_name: str = Field(
        title="Azure Blob Storage account name",
        description="The account's name of the Azure Blob Storage.",
        examples=["airbyte5storage"],
        order=3,
    )
    azure_blob_storage_container_name: str = Field(
        title="Azure blob storage container (Bucket) Name",
        description="The name of the Azure blob storage container.",
        examples=["airbytetescontainername"],
        order=4,
    )
    azure_blob_storage_endpoint: Optional[str] = Field(
        title="Endpoint Domain Name",
        description="This is Azure Blob Storage endpoint domain name. Leave default value (or leave it empty if run container from "
        "command line) to use Microsoft native from example.",
        examples=["blob.core.windows.net"],
        order=11,
    )

    @classmethod
    def schema(cls, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Generates the mapping comprised of the config fields
        """
        schema = super().schema(*args, **kwargs)

        # Hide API processing option until https://github.com/airbytehq/airbyte-platform-internal/issues/10354 is fixed
        processing_options = dpath.util.get(schema, "properties/streams/items/properties/format/oneOf/4/properties/processing/oneOf")
        dpath.util.set(schema, "properties/streams/items/properties/format/oneOf/4/properties/processing/oneOf", processing_options[:1])

        return schema
