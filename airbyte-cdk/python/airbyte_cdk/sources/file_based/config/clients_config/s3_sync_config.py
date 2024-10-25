# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Literal, Optional

from airbyte_cdk.sources.file_based.config.clients_config.base_sync_config import BaseSyncConfig
from pydantic.v1 import Field


class S3SyncConfig(BaseSyncConfig):
    sync_type: Literal["s3"] = Field("s3", const=True)
    bucket: str = Field(description="Name of the S3 bucket where the file(s) exist.", order=7)
    aws_access_key_id: Optional[str] = Field(
        title="AWS Access Key ID",
        default=None,
        description="In order to access private Buckets stored on AWS S3, this connector requires credentials with the proper "
        "permissions. If accessing publicly available data, this field is not necessary.",
        airbyte_secret=True,
        always_show=True,
        order=8,
    )
    aws_secret_access_key: Optional[str] = Field(
        title="AWS Secret Access Key",
        default=None,
        description="In order to access private Buckets stored on AWS S3, this connector requires credentials with the proper "
        "permissions. If accessing publicly available data, this field is not necessary.",
        airbyte_secret=True,
        always_show=True,
        order=9,
    )
    path_prefix: str = Field(
        default="",
        description="By providing a path-like prefix (e.g. myFolder/thisTable/) under which all the relevant files sit, "
        "we can optimize finding these in S3. This is optional but recommended if your bucket contains many "
        "folders/files which you don't need to replicate.",
        order=10,
    )
