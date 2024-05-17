#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import enum


class CredentialsType(enum.Enum):
    IAM_USER = "IAM User"
    IAM_ASSUME_ROLE = "IAM Assume Role"

    @staticmethod
    def from_string(s: str):
        if s == "IAM User":
            return CredentialsType.IAM_USER
        elif s == "IAM Assume Role":
            return CredentialsType.IAM_ASSUME_ROLE
        else:
            raise ValueError(f"Unknown auth mode: {s}")


# class OutputFormat(enum.Enum):
#     PARQUET = "Parquet"
#     JSONL = "JSONL"
#     ICEBERG = "Iceberg"

#     @staticmethod
#     def from_string(s: str):
#         if s == "Parquet":
#             return OutputFormat.PARQUET
#         elif s == "Iceberg":
#             return OutputFormat.ICEBERG

#         return OutputFormat.JSONL


class CompressionCodec(enum.Enum):
    SNAPPY = "SNAPPY"
    # GZIP = "GZIP"
    ZSTD = "ZSTD"
    # UNCOMPRESSED = "UNCOMPRESSED"

    @staticmethod
    def from_config(str: str):
        if str == "SNAPPY":
            return CompressionCodec.SNAPPY
        elif str == "ZSTD":
            return CompressionCodec.ZSTD

        return CompressionCodec.SNAPPY


class PartitionOptions(enum.Enum):
    NONE = "NO PARTITIONING"
    DATE = "DATE"
    YEAR = "YEAR"
    MONTH = "MONTH"
    DAY = "DAY"
    YEAR_MONTH = "YEAR/MONTH"
    YEAR_MONTH_DAY = "YEAR/MONTH/DAY"

    # @staticmethod
    # def from_string(s: str):
    #     if s == "DATE":
    #         return PartitionOptions.DATE
    #     elif s == "YEAR":
    #         return PartitionOptions.YEAR
    #     elif s == "MONTH":
    #         return PartitionOptions.MONTH
    #     elif s == "DAY":
    #         return PartitionOptions.DAY
    #     elif s == "YEAR/MONTH":
    #         return PartitionOptions.YEAR_MONTH
    #     elif s == "YEAR/MONTH/DAY":
    #         return PartitionOptions.YEAR_MONTH_DAY

    #     return PartitionOptions.NONE
    
class IcebergPartitionType(enum.Enum):
    DATE = "day"
    YEAR = "year"
    MONTH = "month"

    @staticmethod
    def from_string(s:str):
        if s == "DATE":
            return IcebergPartitionType.DATE
        elif s == "YEAR":
            return IcebergPartitionType.YEAR
        elif s == "MONTH":
            return IcebergPartitionType.MONTH


class ConnectorConfig:
    def __init__(
        self,
        aws_account_id: str = None,
        region: str = None,
        credentials: dict = None,
        bucket_name: str = None,
        bucket_prefix: str = None,
        format: dict = {},
        glue_database: str = None,
    ):
        self.aws_account_id = aws_account_id
        self.credentials = credentials
        self.credentials_type = CredentialsType.from_string(credentials.get("credentials_title"))
        self.region = region
        self.bucket_name = bucket_name
        self.bucket_prefix = bucket_prefix
    
        self.glue_database = glue_database
        # self.format_type = OutputFormat.from_string(format.get("format_type", OutputFormat.PARQUET.value))
        self.compression_codec = CompressionCodec.from_config(format.get("compression_codec", CompressionCodec.SNAPPY.value))
        self.temp_bucket = format.get("temp_bucket",None)
        self.iceberg_is_partitioned = format.get("partition_by_cursor_field",False)
        if self.iceberg_is_partitioned:
            self.iceberg_partition_type = IcebergPartitionType.from_string(format.get("partitioning"))

        if self.credentials_type == CredentialsType.IAM_USER:
            self.aws_access_key = self.credentials.get("aws_access_key_id")
            self.aws_secret_key = self.credentials.get("aws_secret_access_key")
        # assume the container's service account role
        elif self.credentials_type == CredentialsType.IAM_ASSUME_ROLE:
            pass
        else:
            raise Exception("Auth Mode not recognized.")

    def __str__(self):
        return f"<S3Bucket(AwsAccountId={self.aws_account_id},Region={self.region},Bucket={self.bucket_name}>"
