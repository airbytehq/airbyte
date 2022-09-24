#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from pydantic import BaseModel, Field


class AWSProvidedCredentials(BaseModel):
    "Use AWS Access Key ID and Access Key Secret as credentials. Needs proper permissions for accessing S3-Bucket."

    class Config:
        title = "AWS Access Key ID and Access Key Secret"

    auth_method: str = Field(
        "aws_provided_credentials",
        const=True,
    )
