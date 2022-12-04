#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
from unittest import mock

import pytest
from airbyte_cdk.models import AirbyteCatalog, SyncMode
from source_azure_table.source import SourceAzureTable
from source_azure_table.streams import AzureTableStream

source = SourceAzureTable()
logger = logging.getLogger()


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


# Tests
def test_discover(mocker, config, tables):
    mocker.patch(
        "source_azure_table.azure_table.AzureTableReader.get_tables",
        return_value=tables,
    )

    catalog = source.discover(logger=logger, config=config)
    stream = catalog.streams[0]

    assert isinstance(catalog, AirbyteCatalog)
    assert len(catalog.streams) == 2
    assert stream.json_schema == {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {"PartitionKey": {"type": "string"}},
    }
    assert stream.supported_sync_modes == [SyncMode.full_refresh, SyncMode.incremental]
    assert stream.source_defined_cursor is True
    assert stream.default_cursor_field == ["PartitionKey"]


def test_streams(mocker, config, tables):
    mocker.patch(
        "source_azure_table.azure_table.AzureTableReader.get_tables",
        return_value=tables,
    )
    streams = source.streams(logger=logger, config=config)
    assert len(streams) == 2
    assert all(isinstance(stream, AzureTableStream) for stream in streams)
