#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
class ConnectorConfig:
    def __init__(
        self,
        aws_account_id: str = None,
        region: str = None,
        auth_mode: str = None,
        aws_access_key_id: str = None,
        aws_secret_access_key: str = None,
        role_arn: str = None,
        bucket_name: str = None,
        bucket_prefix: str = None,
        lakeformation_database_name: str = None,
        table_name: str = None,
    ):
        self.aws_account_id = aws_account_id
        self.aws_access_key = aws_access_key_id
        self.aws_secret_key = aws_secret_access_key
        self.auth_mode = auth_mode
        self.role_arn = role_arn
        self.region = region
        self.bucket_name = bucket_name
        self.bucket_prefix = bucket_prefix
        self.lakeformation_database_name = lakeformation_database_name
        self.table_name = table_name

    def __str__(self):
        return f"<S3Bucket(AwsAccountId={self.aws_account_id},Region={self.region},Bucket={self.bucket_name},Auth={self.auth_mode}>"
