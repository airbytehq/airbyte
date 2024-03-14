#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from typing import Any, Dict, Optional

import dpath.util
from airbyte_cdk.sources.file_based.config.abstract_file_based_spec import AbstractFileBasedSpec
from airbyte_cdk.utils import is_cloud_environment
from pydantic import AnyUrl, Field, ValidationError, root_validator


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

    role_arn: Optional[str] = Field(
        title=f"AWS Role ARN",
        default=None,
        description="Specifies the Amazon Resource Name (ARN) of an IAM role that you want to use to perform operations "
        f"requested using this profile. Set the External ID to the Airbyte workspace ID, which can be found in the URL of this page.",
        order=6,
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

    @root_validator
    def validate_optional_args(cls, values):
        aws_access_key_id = values.get("aws_access_key_id")
        aws_secret_access_key = values.get("aws_secret_access_key")
        if (aws_access_key_id or aws_secret_access_key) and not (aws_access_key_id and aws_secret_access_key):
            raise ValidationError(
                "`aws_access_key_id` and `aws_secret_access_key` are both required to authenticate with AWS.", model=Config
            )

        if is_cloud_environment():
            endpoint = values.get("endpoint")
            if endpoint:
                if endpoint.startswith("http://"):  # ignore-https-check
                    raise ValidationError("The endpoint must be a secure HTTPS endpoint.", model=Config)

        return values

    @classmethod
    def schema(cls, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Generates the mapping comprised of the config fields
        """
        schema = super().schema(*args, **kwargs)

        # Hide API processing option until https://github.com/airbytehq/airbyte-platform-internal/issues/10354 is fixed
        processing_options = dpath.util.get(schema, "properties/streams/items/properties/format/oneOf/4/properties/processing/oneOf")
        dpath.util.set(schema, "properties/streams/items/properties/format/oneOf/4/properties/processing/oneOf", processing_options[:1])

        return schema
