#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from typing import Optional

from pydantic import BaseModel, Field

from .source_files_abstract.source import SourceFilesAbstract
from .source_files_abstract.spec import SourceFilesAbstractSpec
from .stream import IncrementalFileStreamS3


class SourceS3Spec(SourceFilesAbstractSpec, BaseModel):
    class Config:
        title = "S3 Source Spec"

    class S3Provider(BaseModel):
        class Config:
            title = "S3: Amazon Web Services"

        bucket: str = Field(description="Name of the S3 bucket where the file(s) exist.")
        aws_access_key_id: Optional[str] = Field(
            default=None,
            description="In order to access private Buckets stored on AWS S3, this connector requires credentials with the proper permissions. If accessing publicly available data, this field is not necessary.",
            airbyte_secret=True,
        )
        aws_secret_access_key: Optional[str] = Field(
            default=None,
            description="In order to access private Buckets stored on AWS S3, this connector requires credentials with the proper permissions. If accessing publicly available data, this field is not necessary.",
            airbyte_secret=True,
        )
        path_prefix: str = Field(
            default="",
            description="By providing a path-like prefix (e.g. myFolder/thisTable/) under which all the relevant files sit, we can optimise finding these in S3. This is optional but recommended if your bucket contains many folders/files.",
        )

        endpoint: str = Field("", description="Endpoint to an S3 compatible service. Leave empty to use AWS.")
        use_ssl: bool = Field(default=None, description="Is remote server using secure SSL/TLS connection")
        verify_ssl_cert: bool = Field(default=None, description="Allow self signed certificates")

    provider: S3Provider


class SourceS3(SourceFilesAbstract):
    stream_class = IncrementalFileStreamS3
    spec_class = SourceS3Spec
    documentation_url = "https://docs.airbyte.io/integrations/sources/s3"
