#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from typing import Optional

from airbyte_cdk.sources.streams.files import FilesSpec
from pydantic import BaseModel, Field


class SourceGoogleCloudStorageSpec(FilesSpec, BaseModel):
    class Config:
        title = "Google Cloud Storage Source Spec"

    class GoogleCloudStorageProvider(BaseModel):
        class Config:
            title = "Google Cloud Storage"

        bucket: str = Field(description="Name of the GCS bucket where the file(s) exist.", order=0)

        service_account_json: Optional[str] = Field(
            title="Service Account JSON",
            default=None,
            description="In order to access private storage, this connector requires credentials with the correct permissions. Follow [the instructions here](https://cloud.google.com/storage/docs/reference/libraries#setting_up_authentication) to create a service account and generate a JSON key file. Then copy the JSON directly into this field. If accessing publicly available data, this field is not necessary.",
            airbyte_secret=True,
            order=1,
        )

    provider: GoogleCloudStorageProvider
