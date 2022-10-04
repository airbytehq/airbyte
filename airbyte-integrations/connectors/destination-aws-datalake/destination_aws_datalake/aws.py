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
from decimal import Decimal
from awswrangler import _data_types
from typing import Dict, List, Optional
from botocore.exceptions import ClientError
from airbyte_cdk.destinations import Destination

from .config_reader import CompressionCodec, CredentialsType, ConnectorConfig, OutputFormat

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
        df[col] = df[col].apply(lambda x: Decimal(str(x)) if str(x) not in ("", "none", "None", " ", "<NA>") else None)
    elif desired_type.lower() in ["float64", "int64"]:
        df[col] = df[col].fillna("")
        df[col] = pd.to_numeric(df[col])
    elif desired_type in ["boolean", "bool"]:
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
            df[col] = df[col].apply(lambda x: int(x) if str(x) not in ("", "none", "None", " ", "<NA>") else None).astype(desired_type)
    return df


# Overwrite to fix type conversion issues from athena to pandas
# These happen when appending data to an existing table. awswrangler
# tries to cast the data types to the existing table schema, examples include:
# Fixes: ValueError: could not convert string to float: ''
# Fixes: TypeError: Need to pass bool-like values
_data_types._cast_pandas_column = _cast_pandas_column


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

    def _pyarrow_types_from_pandas(self, df: pd.DataFrame): # pylint: disable=too-many-branches
        """
        Extract the related Pyarrow data types from any Pandas DataFrame
        and account for data types that can't be automatically casted.
        """
        # Handle exception data types (e.g. Int64, Int32, string)
        cols: List[str] = []
        cols_dtypes: Dict[str, Optional[pa.DataType]] = {}
        for name, dtype in df.dtypes.to_dict().items():
            dtype = str(dtype)
            if dtype == "Int8":
                cols_dtypes[name] = pa.int8()
            elif dtype == "Int16":
                cols_dtypes[name] = pa.int16()
            elif dtype == "Int32":
                cols_dtypes[name] = pa.int32()
            elif dtype == "Int64":
                cols_dtypes[name] = pa.int64()
            elif dtype == "string":
                cols_dtypes[name] = pa.string()
            else:
                cols.append(name)

        # Filling cols_dtypes
        for col in cols:
            logger.debug("Inferring PyArrow type from column: %s", col)
            try:
                schema: pa.Schema = pa.Schema.from_pandas(df=df[[col]], preserve_index=False)

            except (pa.ArrowInvalid, TypeError) as ex:
                # Handle arrays with objects of mixed types
                logger.warning(
                    f"Unable able to infer data type for column {col}, casting column type to string: {ex}"
                )

                cols_dtypes[col] = pa.string()
                df[col].fillna("", inplace=True)
                df[col] = df[col].astype(str)

            else:
                cols_dtypes[col] = schema.field(col).type

        columns_types: Dict[str, pa.DataType]
        columns_types = {n: cols_dtypes[n] for n in list(df.columns)}
        logger.debug("columns_types: %s", columns_types)
        return columns_types

    def _validate_athena_types(self, df: pd.DataFrame):
        pa_columns_types: Dict[str, Optional[pa.DataType]] = self._pyarrow_types_from_pandas(df)

        logger.debug(f"Validating types for {len( pa_columns_types.items())} columns")

        # Cast any bad type to string by default
        for k, v in pa_columns_types.items():
            try:
                t = wr._data_types.pyarrow2athena(dtype=v)
                if "struct<>" in t:
                    logger.warning(f"Empty struct type for column {k} is not supported by Athena. Casting to json string")

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
            use_threads=False,  # True causes s3 NoCredentialsError error
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
            use_threads=False,  # True causes s3 NoCredentialsError error
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
