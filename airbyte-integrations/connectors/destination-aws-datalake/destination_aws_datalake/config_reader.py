#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import enum


class AuthMode(enum.Enum):
    IAM_ROLE = "IAM Role"
    IAM_USER = "IAM User"


class ConnectorConfig:
    def __init__(
        self,
        aws_account_id: str = None,
        region: str = None,
        credentials: dict = None,
        bucket_name: str = None,
        bucket_prefix: str = None,
        lakeformation_database_name: str = None,
        table_name: str = None,
    ):
        self.aws_account_id = aws_account_id
        self.credentials = credentials
        self.credentials_type = credentials.get("credentials_title")
        self.region = region
        self.bucket_name = bucket_name
        self.bucket_prefix = bucket_prefix
        self.lakeformation_database_name = lakeformation_database_name
        self.table_name = table_name

        if self.credentials_type == AuthMode.IAM_USER.value:
            self.aws_access_key = self.credentials.get("aws_access_key_id")
            self.aws_secret_key = self.credentials.get("aws_secret_access_key")
        elif self.credentials_type == AuthMode.IAM_ROLE.value:
            self.role_arn = self.credentials.get("role_arn")
        else:
            raise Exception("Auth Mode not recognized.")

    def __str__(self):
        return f"<S3Bucket(AwsAccountId={self.aws_account_id},Region={self.region},Bucket={self.bucket_name}>"
