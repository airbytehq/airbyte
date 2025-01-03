#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from typing import Literal, Union

from pydantic.v1 import BaseModel, Field

from airbyte_cdk.utils.oneof_option_config import OneOfOptionConfig


class OAuthCredentials(BaseModel):
    class Config(OneOfOptionConfig):
        title = "Authenticate via Google (OAuth)"

    auth_type: Literal["Client"]
    client_id: str = Field(
        title="Client ID",
        description="Client ID",
        airbyte_secret=True,
    )
    client_secret: str = Field(
        title="Client Secret",
        description="Client Secret",
        airbyte_secret=True,
    )
    access_token: str = Field(
        title="Access Token",
        description="Access Token",
        airbyte_secret=True,
    )
    refresh_token: str = Field(
        title="Access Token",
        description="Access Token",
        airbyte_secret=True,
    )


class ServiceAccountCredentials(BaseModel):
    class Config(OneOfOptionConfig):
        title = "Service Account Authentication."

    auth_type: Literal["Service"]
    service_account: str = Field(
        title="Service Account Information.",
        airbyte_secret=True,
        description=(
            'Enter your Google Cloud <a href="https://cloud.google.com/iam/docs/'
            'creating-managing-service-account-keys#creating_service_account_keys">'
            "service account key</a> in JSON format"
        ),
    )


class SourceGCSSpec(BaseModel):
    """
    The SourceGCSSpec class defines the expected input configuration
    for the Google Cloud Storage (GCS) source. It uses Pydantic for data
    validation through the defined data models.

    Note: When this Spec is changed, ensure that the legacy_config_transformer.py
    is also modified to accommodate the changes, as it is responsible for
    converting legacy GCS configs into file based configs using the File-Based CDK.
    """

    gcs_bucket: str = Field(
        title="GCS bucket",
        description="GCS bucket name",
        order=0,
    )

    gcs_path: str = Field(
        title="GCS Path",
        description="GCS path to data",
        order=1,
    )

    credentials: Union[OAuthCredentials, ServiceAccountCredentials] = Field(
        title="Authentication",
        description="Credentials for connecting to the Google Cloud Storage API",
        type="object",
        order=2,
        discriminator="auth_type",
    )
