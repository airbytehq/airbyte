#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import List, Optional, Union

from airbyte_cdk.sources.file_based.config.abstract_file_based_spec import AbstractFileBasedSpec
from airbyte_cdk.sources.file_based.config.avro_format import AvroFormat
from airbyte_cdk.sources.file_based.config.csv_format import CsvFormat
from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig
from airbyte_cdk.sources.file_based.config.jsonl_format import JsonlFormat
from airbyte_cdk.sources.file_based.config.parquet_format import ParquetFormat
from pydantic import AnyUrl, BaseModel, Field, ValidationError, root_validator


class UnstructuredFormat(BaseModel):
    class Config:
        title = "Markdown/PDF/Docx Format (Experimental)"
        schema_extra = {"description": "Extract text from document formats and emit as one record per file."}

    filetype: str = Field(
        "unstructured",
        const=True,
    )


class S3FileBasedStreamConfig(FileBasedStreamConfig):
    format: Union[AvroFormat, CsvFormat, JsonlFormat, ParquetFormat, UnstructuredFormat] = Field(
        title="Format",
        description="The configuration options that are used to alter how to read incoming files that deviate from the standard formatting.",
    )


class Config(AbstractFileBasedSpec):
    """
    NOTE: When this Spec is changed, legacy_config_transformer.py must also be modified to uptake the changes
    because it is responsible for converting legacy S3 v3 configs into v4 configs using the File-Based CDK.
    """

    @classmethod
    def documentation_url(cls) -> AnyUrl:
        return AnyUrl("https://docs.airbyte.com/integrations/sources/s3", scheme="https")

    bucket: str = Field(title="Bucket", description="Name of the S3 bucket where the file(s) exist.", order=0)

    aws_access_key_id: Optional[str] = Field(
        title="AWS Access Key ID",
        default=None,
        description="In order to access private Buckets stored on AWS S3, this connector requires credentials with the proper "
        "permissions. If accessing publicly available data, this field is not necessary.",
        airbyte_secret=True,
        order=2,
    )

    aws_secret_access_key: Optional[str] = Field(
        title="AWS Secret Access Key",
        default=None,
        description="In order to access private Buckets stored on AWS S3, this connector requires credentials with the proper "
        "permissions. If accessing publicly available data, this field is not necessary.",
        airbyte_secret=True,
        order=3,
    )

    endpoint: Optional[str] = Field(
        "", title="Endpoint", description="Endpoint to an S3 compatible service. Leave empty to use AWS.", order=4
    )

    streams: List[S3FileBasedStreamConfig] = Field(
        title="The list of streams to sync",
        description='Each instance of this configuration defines a <a href="https://docs.airbyte.com/cloud/core-concepts#stream">stream</a>. Use this to define which files belong in the stream, their format, and how they should be parsed and validated. When sending data to warehouse destination such as Snowflake or BigQuery, each stream is a separate table.',
        order=10,
    )

    @root_validator
    def validate_optional_args(cls, values):
        aws_access_key_id = values.get("aws_access_key_id")
        aws_secret_access_key = values.get("aws_secret_access_key")
        if (aws_access_key_id or aws_secret_access_key) and not (aws_access_key_id and aws_secret_access_key):
            raise ValidationError(
                "`aws_access_key_id` and `aws_secret_access_key` are both required to authenticate with AWS.", model=Config
            )
        return values
