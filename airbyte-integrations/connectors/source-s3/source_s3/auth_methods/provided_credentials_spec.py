#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from pydantic import BaseModel, Field


class ProvidedCredentials(BaseModel):
    "Use Access Key ID and Access Key Secret as credentials. Needs proper permissions for accessing S3-Bucket"

    class Config:
        title = "Provided Credentials"

    auth_method: str = Field(
        "provided_credentials",
        const=True,
    )
