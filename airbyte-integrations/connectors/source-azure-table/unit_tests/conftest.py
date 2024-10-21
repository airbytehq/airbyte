#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from unittest import mock

import pytest
from source_azure_table.azure_table import AzureTableReader
from source_azure_table.source import SourceAzureTable


# Fixtures
@pytest.fixture
def config():
    return {"storage_account_name": "dummy-value", "storage_access_key": "dummy-value", "storage_endpoint_suffix": "dummy-value"}


@pytest.fixture
def tables():
    table1 = mock.Mock()
    table1.name = "AzureTable1"
    table2 = mock.Mock()
    table2.name = "AzureTable2"

    tables = mock.MagicMock()
    tables.__iter__.return_value = [table1, table2]
    return tables


@pytest.fixture
def source():
    return SourceAzureTable()


@pytest.fixture
def logger():
    return logging.getLogger("airbyte")


@pytest.fixture
def reader(config, logger):
    return AzureTableReader(logger, config)
