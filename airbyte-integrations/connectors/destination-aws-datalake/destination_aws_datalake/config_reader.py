#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import enum


class CredentialsType(enum.Enum):
    IAM_ROLE = "IAM Role"
    IAM_USER = "IAM User"

    @staticmethod
    def from_string(s: str):
        if s == "IAM Role":
            return CredentialsType.IAM_ROLE
        elif s == "IAM User":
            return CredentialsType.IAM_USER
        else:
            raise ValueError(f"Unknown auth mode: {s}")


class OutputFormat(enum.Enum):
    PARQUET = "Parquet"
    JSONL = "JSONL"

    @staticmethod
    def from_string(s: str):
        if s == "Parquet":
            return OutputFormat.PARQUET

        return OutputFormat.JSONL


class CompressionCodec(enum.Enum):
    SNAPPY = "SNAPPY"
    GZIP = "GZIP"
    ZSTD = "ZSTD"
    UNCOMPRESSED = "UNCOMPRESSED"

    @staticmethod
    def from_config(str: str):
        if str == "SNAPPY":
            return CompressionCodec.SNAPPY
        elif str == "GZIP":
            return CompressionCodec.GZIP
        elif str == "ZSTD":
            return CompressionCodec.ZSTD

        return CompressionCodec.UNCOMPRESSED


class PartitionOptions(enum.Enum):
    NONE = "NO PARTITIONING"
    DATE = "DATE"
    YEAR = "YEAR"
    MONTH = "MONTH"
    DAY = "DAY"
    YEAR_MONTH = "YEAR/MONTH"
    YEAR_MONTH_DAY = "YEAR/MONTH/DAY"

    @staticmethod
    def from_string(s: str):
        if s == "DATE":
            return PartitionOptions.DATE
        elif s == "YEAR":
            return PartitionOptions.YEAR
        elif s == "MONTH":
            return PartitionOptions.MONTH
        elif s == "DAY":
            return PartitionOptions.DAY
        elif s == "YEAR/MONTH":
            return PartitionOptions.YEAR_MONTH
        elif s == "YEAR/MONTH/DAY":
            return PartitionOptions.YEAR_MONTH_DAY

        return PartitionOptions.NONE


class ConnectorConfig:
    def __init__(
        self,
        aws_account_id: str = None,
        region: str = None,
        credentials: dict = None,
        bucket_name: str = None,
        bucket_prefix: str = None,
        lakeformation_database_name: str = None,
        lakeformation_database_default_tag_key: str = None,
        lakeformation_database_default_tag_values: str = None,
        lakeformation_governed_tables: bool = False,
        glue_catalog_float_as_decimal: bool = False,
        table_name: str = None,
        format: dict = {},
        partitioning: str = None,
    ):
        self.aws_account_id = aws_account_id
        self.credentials = credentials
        self.credentials_type = CredentialsType.from_string(credentials.get("credentials_title"))
        self.region = region
        self.bucket_name = bucket_name
        self.bucket_prefix = bucket_prefix
        self.lakeformation_database_name = lakeformation_database_name
        self.lakeformation_database_default_tag_key = lakeformation_database_default_tag_key
        self.lakeformation_database_default_tag_values = lakeformation_database_default_tag_values
        self.lakeformation_governed_tables = lakeformation_governed_tables
        self.glue_catalog_float_as_decimal = glue_catalog_float_as_decimal
        self.table_name = table_name

        self.format_type = OutputFormat.from_string(format.get("format_type", OutputFormat.PARQUET.value))
        self.compression_codec = CompressionCodec.from_config(format.get("compression_codec", CompressionCodec.UNCOMPRESSED.value))

        self.partitioning = PartitionOptions.from_string(partitioning)

        if self.credentials_type == CredentialsType.IAM_USER:
            self.aws_access_key = self.credentials.get("aws_access_key_id")
            self.aws_secret_key = self.credentials.get("aws_secret_access_key")
        elif self.credentials_type == CredentialsType.IAM_ROLE:
            self.role_arn = self.credentials.get("role_arn")
        else:
            raise Exception("Auth Mode not recognized.")

    def __str__(self):
        return f"<S3Bucket(AwsAccountId={self.aws_account_id},Region={self.region},Bucket={self.bucket_name}>"
