#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Optional

from airbyte_cdk.sources.file_based.config.abstract_file_based_spec import AbstractFileBasedSpec
from pydantic import AnyUrl, Field


class Config(AbstractFileBasedSpec):
    """
    NOTE: When this Spec is changed, legacy_config_transformer.py must also be modified to uptake the changes
    because it is responsible for converting legacy Azure Blob Storage v0 configs into v1 configs using the File-Based CDK.
    """

    @classmethod
    def documentation_url(cls) -> AnyUrl:
        return AnyUrl("https://docs.airbyte.com/integrations/sources/azure-blob-storage", scheme="https")

    azure_blob_storage_account_name: str = Field(
        title="Azure Blob Storage account name",
        description="The account's name of the Azure Blob Storage.",
        examples=["airbyte5storage"],
        order=2,
    )
    azure_blob_storage_account_key: str = Field(
        title="Azure Blob Storage account key",
        description="The Azure blob storage account key.",
        airbyte_secret=True,
        examples=["Z8ZkZpteggFx394vm+PJHnGTvdRncaYS+JhLKdj789YNmD+iyGTnG+PV+POiuYNhBg/ACS+LKjd%4FG3FHGN12Nd=="],
        order=3,
    )
    azure_blob_storage_container_name: str = Field(
        title="Azure blob storage container (Bucket) Name",
        description="The name of the Azure blob storage container.",
        examples=["airbytetescontainername"],
        order=4,
    )
    azure_blob_storage_endpoint: Optional[str] = Field(
        title="Endpoint Domain Name",
        description="This is Azure Blob Storage endpoint domain name. Leave default value (or leave it empty if run container from "
        "command line) to use Microsoft native from example.",
        examples=["blob.core.windows.net"],
        order=11,
    )
