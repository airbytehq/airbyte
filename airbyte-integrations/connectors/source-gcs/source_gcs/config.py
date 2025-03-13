#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Literal, Union

from pydantic.v1 import AnyUrl, BaseModel, Field

from airbyte_cdk.sources.file_based.config.abstract_file_based_spec import AbstractFileBasedSpec
from airbyte_cdk.utils.oneof_option_config import OneOfOptionConfig


class OAuthCredentials(BaseModel):
    class Config(OneOfOptionConfig):
        title = "Authenticate via Google (OAuth)"

    auth_type: Literal["Client"] = Field("Client", const=True)
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

    auth_type: Literal["Service"] = Field("Service", const=True)
    service_account: str = Field(
        title="Service Account Information.",
        airbyte_secret=True,
        description=(
            'Enter your Google Cloud <a href="https://cloud.google.com/iam/docs/'
            'creating-managing-service-account-keys#creating_service_account_keys">'
            "service account key</a> in JSON format"
        ),
    )


class Config(AbstractFileBasedSpec, BaseModel):
    """
    NOTE: When this Spec is changed, legacy_config_transformer.py must also be
    modified to uptake the changes because it is responsible for converting
    legacy GCS configs into file based configs using the File-Based CDK.
    """

    credentials: Union[OAuthCredentials, ServiceAccountCredentials] = Field(
        title="Authentication",
        description="Credentials for connecting to the Google Cloud Storage API",
        type="object",
        discriminator="auth_type",
        order=0,
    )

    bucket: str = Field(title="Bucket", description="Name of the GCS bucket where the file(s) exist.", order=2)

    @classmethod
    def documentation_url(cls) -> AnyUrl:
        """
        Returns the documentation URL.
        """
        return AnyUrl("https://docs.airbyte.com/integrations/sources/gcs", scheme="https")
