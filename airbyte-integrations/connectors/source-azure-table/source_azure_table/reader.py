#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import re
from typing import Dict, Iterable, List

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import AirbyteStream
from azure.data.tables import TableClient, TableServiceClient

from . import constants


class Reader:
    """
    This reader reads data from given table

    Attributes
    ----------
    logger : AirbyteLogger
        Airbyte's Logger instance
    account_name : str
        The name of your storage account.
    access_key : str
        The access key to your storage account. Read more about access keys here - https://docs.microsoft.com/en-us/azure/storage/common/storage-account-keys-manage?tabs=azure-portal#view-account-access-keys
    endpoint_suffix : str
        The Table service account URL suffix. Read more about suffixes here - https://docs.microsoft.com/en-us/azure/storage/common/storage-configure-connection-string#create-a-connection-string-with-an-endpoint-suffix
    connection_string: str
        storage account connection string created using above params. Read more about connection string here - https://docs.microsoft.com/en-us/azure/storage/common/storage-configure-connection-string#configure-a-connection-string-for-an-azure-storage-account

    Methods
    -------
    get_table_service()
        Returns azure table service client from connection string.

    get_table_client(table_name: str)
        Returns azure table client from connection string.

    get_streams()
        Fetches all tables from storage account and returns them in Airbyte stream.

    """

    def __init__(self, logger: AirbyteLogger, config: dict):
        """
        Parameters
        ----------
        config : dict
            Airbyte's configuration obect

        """
        self.logger = logger
        self.account_name = config[constants.azure_storage_account_name_key_name]
        self.access_key = config[constants.azure_storage_access_key_key_name]
        self.endpoint_suffix = config[constants.azure_storage_endpoint_suffix_key_name]
        self.endpoint = "{}.table.{}".format(self.account_name, self.endpoint_suffix)
        self.connection_string = "DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix={}".format(
            self.account_name, self.access_key, self.endpoint_suffix
        )

    def get_table_service(self) -> TableServiceClient:
        """
        Returns azure table service client from connection string.
        Table service client facilitate interaction with tables. Please read more here - https://docs.microsoft.com/en-us/rest/api/storageservices/operations-on-tables

        """
        try:
            return TableServiceClient.from_connection_string(conn_str=self.connection_string)
        except Exception as e:
            raise Exception(f"An exception occurred: {str(e)}")

    def get_table_client(self, table_name: str) -> TableClient:
        """
        Returns azure table client from connection string.
        Table client facilitate interaction with table entities/rows. Please read more here - https://docs.microsoft.com/en-us/rest/api/storageservices/operations-on-entities

        Parameters
        ----------
        table_name : str
            table name for which you would like create table client for.

        """
        try:
            if not table_name:
                raise Exception("An exception occurred: table name is not valid.")
            return TableClient.from_connection_string(self.connection_string, table_name=table_name)
        except Exception as e:
            raise Exception(f"An exception occurred: {str(e)}")

    def get_streams(self) -> List[AirbyteStream]:
        """
        Fetches all tables from storage account and returns them in Airbyte stream.
        """
        try:
            streams = []
            table_client = self.get_table_service()
            tables_iterator = table_client.list_tables(results_per_page=constants.results_per_page)
            for table in tables_iterator:
                stream_name = table.name
                stream = AirbyteStream(name=stream_name, json_schema=self.get_typed_schema)
                stream.supported_sync_modes = ["full_refresh"]
                streams.append(stream)
            self.logger.info(f"Total {streams.count} streams found.")
            return streams
        except Exception as e:
            raise Exception(f"An exception occurred: {str(e)}")

    @property
    def get_typed_schema(self) -> object:
        """Static schema for tables"""
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {"data": {"type": "object"}, "additionalProperties": {"type": "boolean"}},
        }

    @property
    def stream_name(self) -> str:
        return str(self._client.table_name)

    @property
    def stream_url(self) -> str:
        return str(self._client.url)

    def read(self, client: TableClient, filter_query=None, parameters=None) -> Iterable:
        if filter_query is None:
            return client.list_entities()
        else:
            return client.query_entities(filter=filter_query, results_per_page=constants.results_per_page)

    def get_filter_query(self, stream_name: str, state: Dict[str, any]) -> str:
        watermark = state["stream_name"]
        if watermark is None or watermark is dict:
            return None
        else:
            return f"Timestamp gt datetime'{watermark}'"

    @staticmethod
    def is_table_name_valid(self, name: str) -> bool:
        """Validates the tables name against regex - https://docs.microsoft.com/en-us/rest/api/storageservices/Understanding-the-Table-Service-Data-Model?redirectedfrom=MSDN#characters-disallowed-in-key-fields"""
        return re.match(constants.table_name_regex, name)
