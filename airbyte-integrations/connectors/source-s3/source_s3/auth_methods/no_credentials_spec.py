#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from pydantic import BaseModel, Field


class NoCredentials(BaseModel):
    "For access to public S3-Buckets or non AWS sources no credentials are required. Request will be unsigned."

    class Config:
        title = "No Credentials"

    auth_method: str = Field(
        "no_credentials",
        const=True,
    )
