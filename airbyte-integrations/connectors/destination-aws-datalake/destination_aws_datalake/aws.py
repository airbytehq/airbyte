#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from decimal import Decimal
from typing import Any, Dict, Optional

import awswrangler as wr
import boto3
import botocore
import pandas as pd
from awswrangler import _data_types
from botocore.credentials import AssumeRoleCredentialFetcher, CredentialResolver, DeferredRefreshableCredentials, JSONFileCache
from botocore.exceptions import ClientError
from retrying import retry

from airbyte_cdk.destinations import Destination

from .config_reader import CompressionCodec, ConnectorConfig, CredentialsType, OutputFormat
from .constants import BOOLEAN_VALUES, EMPTY_VALUES


logger = logging.getLogger("airbyte")


def _cast_pandas_column(df: pd.DataFrame, col: str, current_type: str, desired_type: str) -> pd.DataFrame:
    if desired_type == "datetime64":
        df[col] = pd.to_datetime(df[col])
    elif desired_type == "date":
        df[col] = df[col].apply(lambda x: _data_types._cast2date(value=x)).replace(to_replace={pd.NaT: None})
    elif desired_type == "bytes":
        df[col] = df[col].astype("string").str.encode(encoding="utf-8").replace(to_replace={pd.NA: None})
    elif desired_type == "decimal":
        # First cast to string
        df = _cast_pandas_column(df=df, col=col, current_type=current_type, desired_type="string")
        # Then cast to decimal
        df[col] = df[col].apply(lambda x: Decimal(str(x)) if str(x) not in EMPTY_VALUES else None)
    elif desired_type.lower() in ["float64", "int64"]:
        df[col] = df[col].fillna("")
        df[col] = pd.to_numeric(df[col])
    elif desired_type in ["boolean", "bool"]:
        if df[col].dtype in ["string", "O"]:
            df[col] = df[col].fillna("false").apply(lambda x: str(x).lower() in BOOLEAN_VALUES)

        df[col] = df[col].astype(bool)
    else:
        try:
            df[col] = df[col].astype(desired_type)
        except (TypeError, ValueError) as ex:
            if "object cannot be converted to an IntegerDtype" not in str(ex):
                raise ex
            logger.warn(
                "Object cannot be converted to an IntegerDtype. Integer columns in Python cannot contain "
                "missing values. If your input data contains missing values, it will be encoded as floats"
                "which may cause precision loss.",
                UserWarning,
            )
            df[col] = df[col].apply(lambda x: int(x) if str(x) not in EMPTY_VALUES else None).astype(desired_type)
    return df


# Overwrite to fix type conversion issues from athena to pandas
# These happen when appending data to an existing table. awswrangler
# tries to cast the data types to the existing table schema, examples include:
# Fixes: ValueError: could not convert string to float: ''
# Fixes: TypeError: Need to pass bool-like values
_data_types._cast_pandas_column = _cast_pandas_column


# This class created to support refreshing sts role assumption credentials for long running syncs
class AssumeRoleProvider(object):
    METHOD = "assume-role"

    def __init__(self, fetcher):
        self._fetcher = fetcher

    def load(self):
        return DeferredRefreshableCredentials(self._fetcher.fetch_credentials, self.METHOD)

    @staticmethod
    def assume_role_refreshable(
        session: botocore.session.Session, role_arn: str, duration: int = 3600, session_name: str = None
    ) -> botocore.session.Session:
        fetcher = AssumeRoleCredentialFetcher(
            session.create_client,
            session.get_credentials(),
            role_arn,
            extra_args={"DurationSeconds": duration, "RoleSessionName": session_name},
            cache=JSONFileCache(),
        )
        role_session = botocore.session.Session()
        role_session.register_component("credential_provider", CredentialResolver([AssumeRoleProvider(fetcher)]))
        return role_session


class AwsHandler:
    def __init__(self, connector_config: ConnectorConfig, destination: Destination) -> None:
        self._config: ConnectorConfig = connector_config
        self._destination: Destination = destination
        self._session: boto3.Session = None

        self.create_session()
        self.glue_client = self._session.client("glue")
        self.s3_client = self._session.client("s3")
        self.lf_client = self._session.client("lakeformation")

        self._table_type = "GOVERNED" if self._config.lakeformation_governed_tables else "EXTERNAL_TABLE"

    @retry(stop_max_attempt_number=10, wait_random_min=1000, wait_random_max=2000)
    def create_session(self) -> None:
        if self._config.credentials_type == CredentialsType.IAM_USER:
            self._session = boto3.Session(
                aws_access_key_id=self._config.aws_access_key,
                aws_secret_access_key=self._config.aws_secret_key,
                region_name=self._config.region,
            )

        elif self._config.credentials_type == CredentialsType.IAM_ROLE:
            botocore_session = AssumeRoleProvider.assume_role_refreshable(
                session=botocore.session.Session(), role_arn=self._config.role_arn, session_name="airbyte-destination-aws-datalake"
            )
            self._session = boto3.session.Session(region_name=self._config.region, botocore_session=botocore_session)

    def _get_s3_path(self, database: str, table: str) -> str:
        bucket = f"s3://{self._config.bucket_name}"
        if self._config.bucket_prefix:
            bucket += f"/{self._config.bucket_prefix}"

        return f"{bucket}/{database}/{table}/"

    def _get_compression_type(self, compression: CompressionCodec) -> Optional[str]:
        if compression == CompressionCodec.GZIP:
            return "gzip"
        elif compression == CompressionCodec.SNAPPY:
            return "snappy"
        elif compression == CompressionCodec.ZSTD:
            return "zstd"
        else:
            return None

    def _write_parquet(
        self,
        df: pd.DataFrame,
        path: str,
        database: str,
        table: str,
        mode: str,
        dtype: Optional[Dict[str, str]],
        partition_cols: list = None,
    ) -> Any:
        return wr.s3.to_parquet(
            df=df,
            path=path,
            dataset=True,
            database=database,
            table=table,
            glue_table_settings={
                "table_type": self._table_type,
            },
            mode=mode,
            use_threads=False,  # True causes s3 NoCredentialsError error
            catalog_versioning=True,
            boto3_session=self._session,
            partition_cols=partition_cols,
            compression=self._get_compression_type(self._config.compression_codec),
            dtype=dtype,
        )

    def _write_json(
        self,
        df: pd.DataFrame,
        path: str,
        database: str,
        table: str,
        mode: str,
        dtype: Optional[Dict[str, str]],
        partition_cols: list = None,
    ) -> Any:
        return wr.s3.to_json(
            df=df,
            path=path,
            dataset=True,
            database=database,
            table=table,
            glue_table_settings={
                "table_type": self._table_type,
            },
            mode=mode,
            use_threads=False,  # True causes s3 NoCredentialsError error
            orient="records",
            lines=True,
            catalog_versioning=True,
            boto3_session=self._session,
            partition_cols=partition_cols,
            dtype=dtype,
            compression=self._get_compression_type(self._config.compression_codec),
        )

    def _write(
        self, df: pd.DataFrame, path: str, database: str, table: str, mode: str, dtype: Dict[str, str], partition_cols: list = None
    ) -> Any:
        self._create_database_if_not_exists(database)

        if self._config.format_type == OutputFormat.JSONL:
            return self._write_json(df, path, database, table, mode, dtype, partition_cols)

        elif self._config.format_type == OutputFormat.PARQUET:
            return self._write_parquet(df, path, database, table, mode, dtype, partition_cols)

        else:
            raise Exception(f"Unsupported output format: {self._config.format_type}")

    def _create_database_if_not_exists(self, database: str) -> None:
        tag_key = self._config.lakeformation_database_default_tag_key
        tag_values = self._config.lakeformation_database_default_tag_values

        wr.catalog.create_database(name=database, boto3_session=self._session, exist_ok=True)

        if tag_key and tag_values:
            self.lf_client.add_lf_tags_to_resource(
                Resource={
                    "Database": {"Name": database},
                },
                LFTags=[{"TagKey": tag_key, "TagValues": tag_values.split(",")}],
            )

    @retry(stop_max_attempt_number=10, wait_random_min=2000, wait_random_max=3000)
    def head_bucket(self):
        return self.s3_client.head_bucket(Bucket=self._config.bucket_name)

    def table_exists(self, database: str, table: str) -> bool:
        try:
            self.glue_client.get_table(DatabaseName=database, Name=table)
            return True
        except ClientError:
            return False

    def delete_table(self, database: str, table: str) -> bool:
        logger.info(f"Deleting table {database}.{table}")
        return wr.catalog.delete_table_if_exists(database=database, table=table, boto3_session=self._session)

    def delete_table_objects(self, database: str, table: str) -> None:
        path = self._get_s3_path(database, table)
        logger.info(f"Deleting objects in {path}")
        return wr.s3.delete_objects(path=path, boto3_session=self._session)

    def reset_table(self, database: str, table: str) -> None:
        logger.info(f"Resetting table {database}.{table}")
        if self.table_exists(database, table):
            self.delete_table(database, table)
            self.delete_table_objects(database, table)

    def write(self, df: pd.DataFrame, database: str, table: str, dtype: Dict[str, str], partition_cols: list):
        path = self._get_s3_path(database, table)
        return self._write(
            df,
            path,
            database,
            table,
            "overwrite",
            dtype,
            partition_cols,
        )

    def append(self, df: pd.DataFrame, database: str, table: str, dtype: Dict[str, str], partition_cols: list):
        path = self._get_s3_path(database, table)
        return self._write(
            df,
            path,
            database,
            table,
            "append",
            dtype,
            partition_cols,
        )

    def upsert(self, df: pd.DataFrame, database: str, table: str, dtype: Dict[str, str], partition_cols: list):
        path = self._get_s3_path(database, table)
        return self._write(
            df,
            path,
            database,
            table,
            "overwrite_partitions",
            dtype,
            partition_cols,
        )
