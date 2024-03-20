# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Optional

from airbyte_cdk.sources.file_based.config.abstract_file_based_spec import AbstractFileBasedSpec
from pydantic import Field, root_validator, ValidationError


class SourceSFTPBulkSpec(AbstractFileBasedSpec):
    class Config:
        title = "SFTP Bulk Source Spec"

    username: str = Field(title="User Name", description="The server user", order=0)

    password: Optional[str] = Field(title="Password", description="Password", airbyte_secret=True, order=1)
    private_key: Optional[str] = Field(title="Private key", description="The Private key", multiline=True, order=2)
    host: str = Field(title="Host Address", description="The server host address", examples=["www.host.com", "192.0.2.1"], order=3)
    port: int = Field(title="Host Address", description="The server port", default=22, examples=["22"], order=4)
    folder_path: Optional[str] = Field(
        title="Folder Path",
        description="The directory to search files for sync",
        examples=["/logs/2022"],
        order=5,
        default="/",
        pattern_descriptor="/folder_to_sync",
    )

    @classmethod
    def documentation_url(cls) -> str:
        return "https://docs.airbyte.com/integrations/sources/sftp-bulk"

    @root_validator(pre=True)
    def check_password_or_key_presented(cls, values):
        if not any((values.get('password'), values.get('private_key'))):
            raise ValidationError('Either password or private key should be provided')
        return values
