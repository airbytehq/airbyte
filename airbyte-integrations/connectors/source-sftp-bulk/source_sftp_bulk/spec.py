# Copyright (c) 2024 Airbyte, Inc., all rights reserved.


from typing import Literal, Optional, Union

from pydantic.v1 import BaseModel, Field

from airbyte_cdk import OneOfOptionConfig
from airbyte_cdk.sources.file_based.config.abstract_file_based_spec import AbstractFileBasedSpec, DeliverRawFiles, DeliverRecords


class PasswordCredentials(BaseModel):
    class Config(OneOfOptionConfig):
        title = "Authenticate via Password"
        discriminator = "auth_type"

    auth_type: Literal["password"] = Field("password", const=True)
    password: str = Field(title="Password", description="Password", airbyte_secret=True, order=3)


class PrivateKeyCredentials(BaseModel):
    class Config(OneOfOptionConfig):
        title = "Authenticate via Private Key"
        discriminator = "auth_type"

    auth_type: Literal["private_key"] = Field("private_key", const=True)
    private_key: str = Field(title="Private key", description="The Private key", multiline=True, order=4, airbyte_secret=True)


class SourceSFTPBulkSpec(AbstractFileBasedSpec):
    class Config:
        title = "SFTP Bulk Source Spec"

    host: str = Field(title="Host Address", description="The server host address", examples=["www.host.com", "192.0.2.1"], order=2)
    username: str = Field(title="User Name", description="The server user", order=3)
    credentials: Union[PasswordCredentials, PrivateKeyCredentials] = Field(
        title="Authentication",
        description="Credentials for connecting to the SFTP Server",
        discriminator="auth_type",
        type="object",
        order=4,
    )
    port: int = Field(title="Host Address", description="The server port", default=22, examples=["22"], order=5)
    folder_path: Optional[str] = Field(
        title="Folder Path",
        description="The directory to search files for sync",
        examples=["/logs/2022"],
        order=6,
        default="/",
        pattern_descriptor="/folder_to_sync",
    )

    delivery_method: Union[DeliverRecords, DeliverRawFiles] = Field(
        title="Delivery Method",
        discriminator="delivery_type",
        type="object",
        order=7,
        display_type="radio",
        group="advanced",
        default="use_records_transfer",
    )

    @classmethod
    def documentation_url(cls) -> str:
        return "https://docs.airbyte.com/integrations/sources/sftp-bulk"
