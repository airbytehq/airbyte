#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Dict, List, Literal, Mapping, Optional, Union

import dpath.util
from pydantic.v1 import AnyUrl, BaseModel, Field, root_validator
from pydantic.v1.error_wrappers import ValidationError

from airbyte_cdk import OneOfOptionConfig, is_cloud_environment
from airbyte_cdk.sources.file_based.config.abstract_file_based_spec import AbstractFileBasedSpec, DeliverRawFiles, DeliverRecords
from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig


class IAMUserCredentials(BaseModel):
    class Config(OneOfOptionConfig):
        title = "IAM User"
        description = "Authenticate with AWS access keys. This also works with S3-compatible endpoints."
        discriminator = "auth_type"

    auth_type: Literal["iam_user"] = Field("iam_user", const=True)
    aws_access_key_id: str = Field(
        title="AWS Access Key ID",
        description="AWS access key ID for authenticating with a private S3 bucket or S3-compatible endpoint.",
        airbyte_secret=True,
        order=1,
    )
    aws_secret_access_key: str = Field(
        title="AWS Secret Access Key",
        description="AWS secret access key for authenticating with a private S3 bucket or S3-compatible endpoint.",
        airbyte_secret=True,
        order=2,
    )


class IAMRoleCredentials(BaseModel):
    class Config(OneOfOptionConfig):
        title = "IAM Role"
        description = "Authenticate by assuming an IAM role."
        discriminator = "auth_type"

    auth_type: Literal["iam_role"] = Field("iam_role", const=True)
    role_arn: str = Field(
        title="AWS Role ARN",
        description="Specifies the Amazon Resource Name (ARN) of an IAM role that you want to use to perform operations "
        "requested using this profile. Set the External ID to the Airbyte workspace ID, which can be found in the URL of this page.",
        order=1,
    )


class DefaultCredentials(BaseModel):
    class Config(OneOfOptionConfig):
        title = "No Authentication / Default AWS Credentials"
        description = (
            "Use for public buckets, or to rely on the default AWS credential chain (instance profile, IRSA, or environment variables)."
        )
        discriminator = "auth_type"

    auth_type: Literal["default_credentials"] = Field("default_credentials", const=True)


class S3FileBasedStreamConfig(FileBasedStreamConfig):
    """S3-specific stream config that adds a flag to skip the full parse check for Parquet files."""

    skip_full_check_for_parquet: bool = Field(
        title="Skip Full Check for Parquet",
        description=(
            "When enabled, the CHECK operation for Parquet streams will verify file accessibility "
            "but skip the full record-parse step. This avoids out-of-memory errors on large Parquet files."
        ),
        default=False,
    )


class Config(AbstractFileBasedSpec):
    """
    NOTE: When this Spec is changed, legacy_config_transformer.py must also be modified to uptake the changes
    because it is responsible for converting legacy S3 v3 configs into v4 configs using the File-Based CDK.
    """

    @classmethod
    def documentation_url(cls) -> AnyUrl:
        return AnyUrl("https://docs.airbyte.com/integrations/sources/s3", scheme="https")

    credentials: Union[IAMUserCredentials, IAMRoleCredentials, DefaultCredentials] = Field(
        title="Authentication",
        description="Credentials for connecting to S3.",
        discriminator="auth_type",
        type="object",
        order=0,
    )

    bucket: str = Field(title="Bucket", description="Name of the S3 bucket where the file(s) exist.", order=1)

    # Use the extended stream config type but keep parent field metadata via schema patching.
    streams: List[S3FileBasedStreamConfig]

    endpoint: Optional[str] = Field(
        default="",
        title="Endpoint",
        description="Endpoint to an S3 compatible service. Leave empty to use AWS.",
        examples=["my-s3-endpoint.com", "https://my-s3-endpoint.com"],
        order=4,
    )

    region_name: Optional[str] = Field(
        title="AWS Region",
        default=None,
        description="AWS region where the S3 bucket is located. If not provided, the region will be determined automatically.",
        order=5,
    )

    delivery_method: DeliverRecords | DeliverRawFiles = Field(
        title="Delivery Method",
        discriminator="delivery_type",
        type="object",
        order=7,
        display_type="radio",
        group="advanced",
        default="use_records_transfer",
    )

    @root_validator
    def validate_optional_args(cls, values):
        if is_cloud_environment():
            endpoint = values.get("endpoint")
            if endpoint:
                if endpoint.startswith("http://"):  # ignore-https-check
                    raise ValidationError("The endpoint must be a secure HTTPS endpoint.", model=Config)

        return values

    @staticmethod
    def migrate_legacy_credentials(config: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
        if "credentials" in config:
            return None

        migrated_config = dict(config)
        aws_access_key_id = migrated_config.pop("aws_access_key_id", None)
        aws_secret_access_key = migrated_config.pop("aws_secret_access_key", None)
        role_arn = migrated_config.pop("role_arn", None)

        if role_arn:
            credentials = {"auth_type": "iam_role", "role_arn": role_arn}
        elif aws_access_key_id or aws_secret_access_key:
            credentials = {"auth_type": "iam_user"}
            if aws_access_key_id:
                credentials["aws_access_key_id"] = aws_access_key_id
            if aws_secret_access_key:
                credentials["aws_secret_access_key"] = aws_secret_access_key
        else:
            credentials = {"auth_type": "default_credentials"}

        migrated_config["credentials"] = credentials
        return migrated_config

    @classmethod
    def schema(cls, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Generates the mapping comprised of the config fields
        """
        schema = super().schema(*args, **kwargs)

        schema["properties"]["start_date"]["order"] = 3

        # Keep parent streams metadata to avoid drift, then inject the S3-specific flag.
        parent_schema = AbstractFileBasedSpec.schema()
        schema["properties"]["streams"] = parent_schema["properties"]["streams"]
        schema["properties"]["streams"]["title"] = "Streams"
        schema["properties"]["streams"]["order"] = 2

        s3_stream_schema = S3FileBasedStreamConfig.schema(*args, **kwargs)
        skip_prop = s3_stream_schema["properties"]["skip_full_check_for_parquet"]
        stream_item_props = schema["properties"]["streams"]["items"]["properties"]
        stream_item_props["name"]["order"] = 0
        stream_item_props["format"]["order"] = 1
        stream_item_props["skip_full_check_for_parquet"] = skip_prop

        # Hide API processing option until https://github.com/airbytehq/airbyte-platform-internal/issues/10354 is fixed
        processing_options = dpath.util.get(schema, "properties/streams/items/properties/format/oneOf/4/properties/processing/oneOf")
        dpath.util.set(schema, "properties/streams/items/properties/format/oneOf/4/properties/processing/oneOf", processing_options[:1])

        return schema
