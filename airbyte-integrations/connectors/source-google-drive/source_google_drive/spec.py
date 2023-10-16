#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Optional

from pydantic import BaseModel, Field
from airbyte_cdk.sources.file_based.config.abstract_file_based_spec import AbstractFileBasedSpec



class SourceGoogleDriveSpec(AbstractFileBasedSpec, BaseModel):
    class Config:
        title = "Google Drive Source Spec"

    folder_url: str = Field(description="URL for the folder you want to sync", order=0)

    service_account_json: str = Field(
        description="Service Account JSON",
        airbyte_secret=True,
        order=1,
    )

    @classmethod
    def documentation_url(cls) -> str:
       return "https://docs.airbyte.com/integrations/sources/google-drive"

