#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import List, Optional

from airbyte_cdk.sources.file_based.config.abstract_file_based_spec import AbstractFileBasedSpec
from airbyte_cdk.sources.file_based.config.csv_format import CsvFormat
from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig
from pydantic import AnyUrl, Field


class SourceGCSStreamConfig(FileBasedStreamConfig):
    name: str = Field(title="Name", description="The name of the stream.", order=0)
    globs: Optional[List[str]] = Field(
        title="Globs",
        description="The pattern used to specify which files should be selected from the file system. For more information on glob "
        'pattern matching look <a href="https://en.wikipedia.org/wiki/Glob_(programming)">here</a>.',
        order=1,
    )
    format: CsvFormat = Field(
        title="Format",
        description="The configuration options that are used to alter how to read incoming files that deviate from "
        "the standard formatting.",
        order=2,
    )
    legacy_prefix: Optional[str] = Field(
        title="Legacy Prefix",
        description="The path prefix configured in previous versions of the GCS connector. "
        "This option is deprecated in favor of a single glob.",
        airbyte_hidden=True,
    )


class Config(AbstractFileBasedSpec):
    """
    NOTE: When this Spec is changed, legacy_config_transformer.py must also be
    modified to uptake the changes because it is responsible for converting
    legacy GCS configs into file based configs using the File-Based CDK.
    """

    service_account: str = Field(
        title="Service Account Information",
        airbyte_secret=True,
        description=(
            "Enter your Google Cloud "
            '<a href="https://cloud.google.com/iam/docs/creating-managing-service-account-keys#creating_service_account_keys">'
            "service account key</a> in JSON format"
        ),
        order=0,
    )

    bucket: str = Field(title="Bucket", description="Name of the GCS bucket where the file(s) exist.", order=2)

    streams: List[SourceGCSStreamConfig] = Field(
        title="The list of streams to sync",
        description=(
            "Each instance of this configuration defines a <a href=https://docs.airbyte.com/cloud/core-concepts#stream>stream</a>. "
            "Use this to define which files belong in the stream, their format, and how they should be "
            "parsed and validated. When sending data to warehouse destination such as Snowflake or "
            "BigQuery, each stream is a separate table."
        ),
        order=3,
    )

    @classmethod
    def documentation_url(cls) -> AnyUrl:
        """
        Returns the documentation URL.
        """
        return AnyUrl("https://docs.airbyte.com/integrations/sources/gcs", scheme="https")

    @staticmethod
    def replace_enum_allOf_and_anyOf(schema):
        """
        Replace allOf with anyOf when appropriate in the schema with one value.
        """
        objects_to_check = schema["properties"]["streams"]["items"]["properties"]["format"]
        if len(objects_to_check.get("allOf", [])) == 1:
            objects_to_check["anyOf"] = objects_to_check.pop("allOf")

        return super(Config, Config).replace_enum_allOf_and_anyOf(schema)

    @staticmethod
    def remove_discriminator(schema) -> None:
        pass
