#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from pydantic import BaseModel, Field


class SourceGCSSpec(BaseModel):
    """
    The SourceGCSSpec class defines the expected input configuration
    for the Google Cloud Storage (GCS) source. It uses Pydantic for data
    validation through the defined data models.

    Note: When this Spec is changed, ensure that the legacy_config_transformer.py
    is also modified to accommodate the changes, as it is responsible for
    converting legacy GCS configs into file based configs using the File-Based CDK.
    """

    gcs_bucket: str = Field(
        title="GCS bucket",
        description="GCS bucket name",
        order=0,
    )

    gcs_path: str = Field(
        title="GCS Path",
        description="GCS path to data",
        order=1,
    )

    service_account: str = Field(
        title="Service Account Information.",
        airbyte_secret=True,
        description=(
            'Enter your Google Cloud <a href="https://cloud.google.com/iam/docs/'
            'creating-managing-service-account-keys#creating_service_account_keys">'
            "service account key</a> in JSON format"
        ),
    )
