from typing import Any, Dict, Literal, Union, List

from airbyte_cdk import OneOfOptionConfig
from airbyte_cdk.sources.file_based.file_based_source import AbstractFileBasedSpec
from pydantic import BaseModel, Field, AnyUrl


class OAuthCredentials(BaseModel):
    class Config(OneOfOptionConfig):
        title = "OAuth"
        discriminator = "auth_type"

    auth_type: Literal["OAuth"] = Field("OAuth", const=True)
    access_token: str = Field(
        title="Access Token",
        description="OAuth access token",
        airbyte_secret=True,
    )
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


class PATCredentials(BaseModel):
    class Config(OneOfOptionConfig):
        title = "Personal Access Token"
        discriminator = "auth_type"

    auth_type: Literal["PAT"] = Field("PAT", const=True)
    personal_access_token: str = Field(
        title="Personal Access Tokens",
        description='Log into GitHub and then generate a <a href="https://github.com/settings/tokens">personal access token</a>. To load balance your API quota consumption across multiple API tokens, input multiple tokens separated with ","',
        airbyte_secret=True,
    )


class SourceGithubFilesSpec(AbstractFileBasedSpec, BaseModel):
    class Config:
        title = "Github files Source Spec"

    credentials: Union[OAuthCredentials, PATCredentials] = Field(
        title="Authentication", description="Credentials for connecting to the Github", discriminator="auth_type", type="object", order=0
    )

    repositories: List[str] = Field(
        title="Repositories",
        description="List of repositories to sync",
        examples=["airbytehq/airbyte", "airbytehq/another-repo"],
        type="array",
        order=1,
    )

    @classmethod
    def documentation_url(cls) -> AnyUrl:
        """
        :return: link to docs page for this source e.g. "https://docs.airbyte.com/integrations/sources/s3"
        """
        return "https://google.com"

    # streams: List[UnstructuredFileBasedConfig] = Field(
    #     title="The list of streams to sync",
    #     description="One stream",
    #     order=10,
    # )
