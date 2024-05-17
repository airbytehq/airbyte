import awswrangler as wr
import logging
import boto3
from .config_reader import ConnectorConfig,CredentialsType
from airbyte_cdk.models import DestinationSyncMode,ConfiguredAirbyteStream
import string
import random
from airbyte_cdk import AirbyteLogger
from pandas import DataFrame
import pandas as pd
from airbyte_cdk.destinations import Destination
from retrying import retry
from botocore.exceptions import ClientError
from typing import Any, Dict, List, Optional, Tuple, Union

logger = logging.getLogger('airbyte')


class Handler:

    def __init__(self,config:ConnectorConfig,destination: Destination) -> None:
        
        self._config: ConnectorConfig = config
        self._destination: Destination = destination
        self._session: boto3.Session = None

        self.create_session()
        self.glue_client = self._session.client("glue")
        self.s3_client = self._session.client("s3")

        self.temp_bucket = self._config.temp_bucket
        self.temp_table_name = f"_temp_{''.join(random.choices(string.ascii_letters, k=10))}"
        self.temp_s3_path = f"s3://{self.temp_bucket}/{self.temp_table_name}/"
        self.glue_database_name = self._config.glue_database
        self.glue_catalog_uri = f"s3://{config.bucket_name}/{config.bucket_prefix}"

        self.glue_temp_database_name = 'airbyte_temp_db'

    @retry(stop_max_attempt_number=10, wait_random_min=1000, wait_random_max=2000)
    def create_session(self) -> None:
        if self._config.credentials_type == CredentialsType.IAM_USER:
            self._session = boto3.Session(
                aws_access_key_id=self._config.aws_access_key,
                aws_secret_access_key=self._config.aws_secret_key,
                region_name=self._config.region,
            )
        elif self._config.credentials_type == CredentialsType.IAM_ASSUME_ROLE:
            self._session = boto3.Session(
                region_name=self._config.region
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

    def _create_destination_table(self,df):

        columns = self._get_columns(df=df)

        return columns

    # create a table to store the temp data
    def create_temp_athena_table(self,df:DataFrame) -> None:

        # create a temp database
        sql = f"create database if not exists {self.glue_temp_database_name}"
        wr.athena.start_query_execution(sql=sql,wait=True)

        if len(df.index) > 0:
            wr.s3.to_parquet(
                df=df,
                dataset=True,
                database=self.glue_temp_database_name,
                path=self.temp_s3_path,
                table=self.temp_table_name,
                mode='append'
            )

    def temp_table_cleanup(self) -> None:

        # drop the temp athena table if exists
        try:
            wr.athena.describe_table(table=self.temp_table_name,database=self.glue_temp_database_name)
            drop_table_query = f"drop table `{self.temp_table_name}`"
            wr.athena.start_query_execution(
                sql=drop_table_query,
                database=self.glue_temp_database_name,
                wait=True
            )

            # delete the data from s3
            s3 = boto3.resource('s3')
            bucket = s3.Bucket(self.temp_bucket)
            bucket.objects.filter(Prefix=f"{self.temp_table_name}/").delete()

            # drop the temp database
            drop_db_query = f"drop dabase {self.glue_temp_database_name}"
            wr.athena.start_query_execution(sql=drop_db_query,wait=True)
        except Exception as e:
            logger.info(f"the table {self.temp_table_name} doesn't exist")

        return True