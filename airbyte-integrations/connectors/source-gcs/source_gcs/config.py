#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.sources.file_based.config.abstract_file_based_spec import AbstractFileBasedSpec
from pydantic import AnyUrl, Field, ValidationError, root_validator


class Config(AbstractFileBasedSpec):
    """
    NOTE: When this Spec is changed, legacy_config_transformer.py must also be
    modified to uptake the changes because it is responsible for converting
    legacy GCS configs into file based configs using the File-Based CDK.
    """

    @classmethod
    def documentation_url(cls) -> AnyUrl:
        """
        Returns the documentation URL.
        """
        return AnyUrl("https://docs.airbyte.com/integrations/sources/gcs", scheme="https")

    bucket: str = Field(title="Bucket", description="Name of the GCS bucket where the file(s) exist.", order=0)

    service_account: str = Field(
        title="Service Account Information.",
        description=(
            "Enter your Google Cloud "
            '<a href="https://cloud.google.com/iam/docs/creating-managing-service-account-keys#creating_service_account_keys">'
            "service account key</a> in JSON format"
        ),
    )
