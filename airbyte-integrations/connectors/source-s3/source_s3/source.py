#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Optional

from pydantic import BaseModel, Field

from .source_files_abstract.spec import SourceFilesAbstractSpec


class SourceS3Spec(SourceFilesAbstractSpec, BaseModel):
    class Config:
        title = "S3 Source Spec"

    class S3Provider(BaseModel):
        class Config:
            title = "S3: Amazon Web Services"
            # SourceFilesAbstractSpec field are ordered 10 apart to allow subclasses to insert their own spec's fields interspersed
            schema_extra = {"order": 11, "description": "Use this to load files from S3 or S3-compatible services"}

        bucket: str = Field(description="Name of the S3 bucket where the file(s) exist.", order=0)
        aws_access_key_id: Optional[str] = Field(
            title="AWS Access Key ID",
            default=None,
            description="In order to access private Buckets stored on AWS S3, this connector requires credentials with the proper "
            "permissions. If accessing publicly available data, this field is not necessary.",
            airbyte_secret=True,
            always_show=True,
            order=1,
        )
        aws_secret_access_key: Optional[str] = Field(
            title="AWS Secret Access Key",
            default=None,
            description="In order to access private Buckets stored on AWS S3, this connector requires credentials with the proper "
            "permissions. If accessing publicly available data, this field is not necessary.",
            airbyte_secret=True,
            always_show=True,
            order=2,
        )
        role_arn: Optional[str] = Field(
            title=f"AWS Role ARN",
            default=None,
            description="Specifies the Amazon Resource Name (ARN) of an IAM role that you want to use to perform operations "
            f"requested using this profile. Set the External ID to the Airbyte workspace ID, which can be found in the URL of this page.",
            always_show=True,
            order=7,
        )
        path_prefix: str = Field(
            default="",
            description="By providing a path-like prefix (e.g. myFolder/thisTable/) under which all the relevant files sit, "
            "we can optimize finding these in S3. This is optional but recommended if your bucket contains many "
            "folders/files which you don't need to replicate.",
            order=3,
        )

        endpoint: str = Field("", description="Endpoint to an S3 compatible service. Leave empty to use AWS.", order=4)
        region_name: Optional[str] = Field(
            title="AWS Region",
            default=None,
            description="AWS region where the S3 bucket is located. If not provided, the region will be determined automatically.",
            order=5,
        )
        start_date: Optional[str] = Field(
            title="Start Date",
            description="UTC date and time in the format 2017-01-25T00:00:00Z. Any file modified before this date will not be replicated.",
            examples=["2021-01-01T00:00:00Z"],
            format="date-time",
            pattern="^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$",
            order=6,
        )

    provider: S3Provider
