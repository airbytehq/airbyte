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
from typing import Dict, List, Optional
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

    def _pyarrow_types_from_pandas(  # pylint: disable=too-many-branches
        self, df: pd.DataFrame, index: bool, ignore_cols: Optional[List[str]] = None, index_left: bool = False
    ) -> Dict[str, pa.DataType]:
        """
        Extract the related Pyarrow data types from any Pandas DataFrame
        and account for data types that can't be automatically casted.
        """
        # Handle exception data types (e.g. Int64, Int32, string)
        ignore_cols = [] if ignore_cols is None else ignore_cols
        cols: List[str] = []
        cols_dtypes: Dict[str, Optional[pa.DataType]] = {}
        for name, dtype in df.dtypes.to_dict().items():
            dtype = str(dtype)
            if name in ignore_cols:
                cols_dtypes[name] = None
            elif dtype == "Int8":
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

            except pa.ArrowInvalid as ex:
                # Handle arrays with objects of mixed types
                logger.warning(f"Invalid arrow type, unable able to infer data type for column {col}, casting DataFrame column to json string: {ex}")

                cols_dtypes[col] = pa.string()
                df[col].fillna("", inplace=True)
                df[col] = df[col].apply(lambda x: json.dumps(x))

            except TypeError as ex:
                msg = str(ex)
                if " is required (got type " in msg:
                    raise TypeError(
                        f"The {col} columns has a too generic data type ({df[col].dtype}) and seems "
                        f"to have mixed data types ({msg}). "
                        "Please, cast this columns with a more deterministic data type "
                        f"(e.g. df['{col}'] = df['{col}'].astype('string')) or "
                        "pass the column schema as argument"
                        f"(e.g. dtype={{'{col}': 'string'}}"
                    ) from ex
                raise

            else:
                cols_dtypes[col] = schema.field(col).type

        # Filling indexes
        indexes: List[str] = []
        if index is True:
            # Get index columns
            try:
                fields = pa.Schema.from_pandas(df=df[[]], preserve_index=True)
            except AttributeError as ae:
                if "'Index' object has no attribute 'head'" not in str(ae):
                    raise ae
                # Get index fields from a new df with only index columns
                # Adding indexes as columns via .reset_index() because
                # pa.Schema.from_pandas(.., preserve_index=True) fails with
                # "'Index' object has no attribute 'head'" if using extension
                # dtypes on pandas 1.4.x
                fields = pa.Schema.from_pandas(df=df.reset_index().drop(columns=cols), preserve_index=False)
            for field in fields:
                name = str(field.name)
                logger.debug("Inferring PyArrow type from index: %s", name)
                cols_dtypes[name] = field.type
                indexes.append(name)

        # Merging Index
        sorted_cols: List[str] = indexes + list(df.columns) if index_left is True else list(df.columns) + indexes

        # Filling schema
        columns_types: Dict[str, pa.DataType]
        columns_types = {n: cols_dtypes[n] for n in sorted_cols}
        logger.debug("columns_types: %s", columns_types)
        return columns_types

    def _validate_athena_types(self, df: pd.DataFrame):
        casts = {}
        pa_columns_types: Dict[str, Optional[pa.DataType]] = self._pyarrow_types_from_pandas(
            df=df, index=False, ignore_cols=list(casts.keys()), index_left=False
        )

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
