#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Iterable

from airbyte_cdk.logger import AirbyteLogger
from azure.core.paging import ItemPaged
from azure.data.tables import TableClient, TableServiceClient

from . import constants


class AzureTableReader:
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
    get_table_service_client()
        Returns azure table service client from connection string.

    get_table_client(table_name: str)
        Returns azure table client from connection string.

    get_tables()
        Fetches all tables from storage account

    read_table()
        Reads data from an Azure table

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
        self.connection_string = "DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix={}".format(
            self.account_name, self.access_key, self.endpoint_suffix
        )

    def get_table_service_client(self) -> TableServiceClient:
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

    def get_tables(self) -> ItemPaged:
        """
        Fetches all tables from storage account and returns them in Airbyte stream.
        """
        try:
            table_service_client = self.get_table_service_client()
            tables_iterator = table_service_client.list_tables(results_per_page=constants.results_per_page)
            return tables_iterator
        except Exception as e:
            raise Exception(f"An exception occurred: {str(e)}")

    def read_table(self, table_client: TableClient, filter_query: str = None) -> Iterable:
        """
        Reads data from an Azure table.

        Parameters
        ----------
        table_client : TableClient
            table client object to be able to access querying methods.

        filter_query : str
            either None or a query to pull data from table storage (based on the PartitionKey)
        """
        if filter_query is None:
            return table_client.list_entities()
        else:
            return table_client.query_entities(query_filter=filter_query, results_per_page=constants.results_per_page)
