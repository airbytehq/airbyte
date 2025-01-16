#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Any, Dict, Literal, Union

import dpath.util
from pydantic.v1 import BaseModel, Field

from airbyte_cdk import OneOfOptionConfig
from airbyte_cdk.sources.file_based.config.abstract_file_based_spec import AbstractFileBasedSpec


class OAuthCredentials(BaseModel):
    class Config(OneOfOptionConfig):
        title = "Authenticate via Google (OAuth)"
        discriminator = "auth_type"

    auth_type: Literal["Client"] = Field("Client", const=True)
    client_id: str = Field(
        title="Client ID",
        description="Client ID for the Google Drive API",
        airbyte_secret=True,
    )
    client_secret: str = Field(
        title="Client Secret",
        description="Client Secret for the Google Drive API",
        airbyte_secret=True,
    )
    refresh_token: str = Field(
        title="Refresh Token",
        description="Refresh Token for the Google Drive API",
        airbyte_secret=True,
    )


class ServiceAccountCredentials(BaseModel):
    class Config(OneOfOptionConfig):
        title = "Service Account Key Authentication"
        discriminator = "auth_type"

    auth_type: Literal["Service"] = Field("Service", const=True)
    service_account_info: str = Field(
        title="Service Account Information",
        description='The JSON key of the service account to use for authorization. Read more <a href="https://cloud.google.com/iam/docs/creating-managing-service-account-keys#creating_service_account_keys">here</a>.',
        airbyte_secret=True,
    )


class SourceGoogleDriveSpec(AbstractFileBasedSpec, BaseModel):
    class Config:
        title = "Google Drive Source Spec"

    folder_url: str = Field(
        description="URL for the folder you want to sync. Using individual streams and glob patterns, it's possible to only sync a subset of all files located in the folder.",
        examples=["https://drive.google.com/drive/folders/1Xaz0vXXXX2enKnNYU5qSt9NS70gvMyYn"],
        order=0,
        pattern="^https://drive.google.com/.+",
        pattern_descriptor="https://drive.google.com/drive/folders/MY-FOLDER-ID",
    )

    credentials: Union[OAuthCredentials, ServiceAccountCredentials] = Field(
        title="Authentication", description="Credentials for connecting to the Google Drive API", discriminator="auth_type", type="object"
    )

    @classmethod
    def documentation_url(cls) -> str:
        return "https://docs.airbyte.com/integrations/sources/google-drive"

    @classmethod
    def schema(cls, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Generates the mapping comprised of the config fields
        """
        schema = super().schema(*args, **kwargs)

        # Remove legacy settings
        dpath.util.delete(schema, "properties/streams/items/properties/legacy_prefix")
        dpath.util.delete(schema, "properties/streams/items/properties/format/oneOf/*/properties/inference_type")

        # Hide API processing option until https://github.com/airbytehq/airbyte-platform-internal/issues/10354 is fixed
        processing_options = dpath.util.get(schema, "properties/streams/items/properties/format/oneOf/4/properties/processing/oneOf")
        dpath.util.set(schema, "properties/streams/items/properties/format/oneOf/4/properties/processing/oneOf", processing_options[:1])

        return schema
