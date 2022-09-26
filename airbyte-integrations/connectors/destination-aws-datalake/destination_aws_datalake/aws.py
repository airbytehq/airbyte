#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
import boto3
import logging
import pandas as pd
import pyarrow as pa
import awswrangler as wr

from retrying import retry
from typing import Dict, Optional
from botocore.exceptions import ClientError
from airbyte_cdk.destinations import Destination

from .config_reader import CompressionCodec, CredentialsType, ConnectorConfig, OutputFormat

logger = logging.getLogger("airbyte")


class AwsHandler:
    def __init__(self, connector_config: ConnectorConfig, destination: Destination):
        self._config: ConnectorConfig = connector_config
        self._destination: Destination = destination
        self._session: boto3.Session = None

        self.create_session()
        self.glue_client = self._session.client("glue")
        self.s3_client = self._session.client("s3")

    @retry(stop_max_attempt_number=10, wait_random_min=1000, wait_random_max=2000)
    def create_session(self):
        if self._config.credentials_type == CredentialsType.IAM_USER:
            self._session = boto3.Session(
                aws_access_key_id=self._config.aws_access_key,
                aws_secret_access_key=self._config.aws_secret_key,
                region_name=self._config.region,
            )

        elif self._config.credentials_type == CredentialsType.IAM_ROLE:
            client = boto3.client("sts")
            role = client.assume_role(
                RoleArn=self._config.role_arn,
                RoleSessionName="airbyte-destination-aws-datalake",
            )
            creds = role.get("Credentials", {})
            self._session = boto3.Session(
                aws_access_key_id=creds.get("AccessKeyId"),
                aws_secret_access_key=creds.get("SecretAccessKey"),
                aws_session_token=creds.get("SessionToken"),
                region_name=self._config.region,
            )

    def _get_compression_type(self, compression: CompressionCodec):
        if compression == CompressionCodec.GZIP:
            return "gzip"
        elif compression == CompressionCodec.SNAPPY:
            return "snappy"
        elif compression == CompressionCodec.ZSTD:
            return "zstd"
        else:
            return None

    def _validate_athena_types(self, df: pd.DataFrame):
        casts = {}
        pa_columns_types: Dict[str, Optional[pa.DataType]] = wr._data_types.pyarrow_types_from_pandas(
            df=df, index=False, ignore_cols=list(casts.keys()), index_left=False
        )

        logger.debug(f"Validating types for {len( pa_columns_types.items())} columns")

        # Cast any bad type to string by default
        for k, v in pa_columns_types.items():
            try:
                t = wr._data_types.pyarrow2athena(dtype=v)
                if "struct<>" in t:
                    logger.warning(f"Empty struct type for column {k} is not supported by Athena. Casting to string")

                    df[k].fillna("", inplace=True)
                    df[k] = df[k].apply(lambda x: json.dumps(x))

            except wr.exceptions.UndetectedType as ex:
                logger.warning(
                    "Impossible to infer the equivalent Athena data type "
                    f"for the {k} column. "
                    "It is completely empty (only null values) "
                    f"and has a too generic data type ({df[k].dtype}). "
                    "Casting it to string."
                )

                df[k].fillna("", inplace=True)
                df[k] = df[k].astype(str)

    def _write_parquet(self, df: pd.DataFrame, path: str, database: str, table: str, mode: str, partition_cols: list = None):
        return wr.s3.to_parquet(
            df=df,
            path=path,
            dataset=True,
            database=database,
            table=table,
            table_type="GOVERNED",
            mode=mode,
            use_threads=False, # True causes s3 NoCredentialsError error
            catalog_versioning=True,
            boto3_session=self._session,
            concurrent_partitioning=True,
            partition_cols=partition_cols,
            compression=self._get_compression_type(self._config.compression_codec),
        )

    def _write_json(self, df: pd.DataFrame, path: str, database: str, table: str, mode: str, partition_cols: list = None):
        return wr.s3.to_json(
            df=df,
            path=path,
            dataset=True,
            database=database,
            table=table,
            table_type="GOVERNED",
            mode=mode,
            use_threads=False, # True causes s3 NoCredentialsError error
            orient="records",
            lines=True,
            catalog_versioning=True,
            boto3_session=self._session,
            concurrent_partitioning=True,
            partition_cols=partition_cols,
            # Compression causes error: https://github.com/aws/aws-sdk-pandas/pull/1585
            # compression=self._get_compression_type(self._config.compression_codec),
        )

    def _write(self, df: pd.DataFrame, path: str, database: str, table: str, mode: str, partition_cols: list = None):
        self._validate_athena_types(df)
        self._create_database_if_not_exists(database)

        if self._config.format_type == OutputFormat.JSONL:
            return self._write_json(df, path, database, table, mode, partition_cols)

        elif self._config.format_type == OutputFormat.PARQUET:
            return self._write_parquet(df, path, database, table, mode, partition_cols)

        else:
            raise Exception(f"Unsupported output format: {self._config.format_type}")

    def _create_database_if_not_exists(self, database: str):
        return wr.catalog.create_database(name=database, boto3_session=self._session, exist_ok=True)

    @retry(stop_max_attempt_number=10, wait_random_min=2000, wait_random_max=3000)
    def head_bucket(self):
        return self.s3_client.head_bucket(Bucket=self._config.bucket_name)

    def table_exists(self, database: str, table: str) -> bool:
        try:
            self.glue_client.get_table(DatabaseName=database, Name=table)
            return True
        except ClientError as e:
            return False

    def delete_table(self, database: str, table: str) -> bool:
        logger.info(f"Deleting table {database}.{table}")
        if self.table_exists(database, table):
            return wr.catalog.delete_table_if_exists(database=database, table=table, boto3_session=self._session)
        return True

    def write(self, df: pd.DataFrame, path: str, database: str, table: str, partition_cols: list):
        return self._write(
            df,
            path,
            database,
            table,
            "overwrite",
            partition_cols,
        )

    def append(self, df: pd.DataFrame, path: str, database: str, table: str, partition_cols: list):
        return self._write(
            df,
            path,
            database,
            table,
            "append",
            partition_cols,
        )

    def upsert(self, df: pd.DataFrame, path: str, database: str, table: str, partition_cols: list):
        return self._write(
            df,
            path,
            database,
            table,
            "overwrite_partitions",
            partition_cols,
        )
