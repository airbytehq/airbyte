#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from pydantic import BaseModel, Field


class AWSDefaultCredentials(BaseModel):
    'Use default <a href="https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html#configuring-credentials" target="_blank">AWS credential provider</html> chain (such as EC2 instance profile).'

    class Config:
        title = "AWS Default Credential Provider Chain"

    auth_method: str = Field(
        "aws_default_credentials",
        const=True,
    )
