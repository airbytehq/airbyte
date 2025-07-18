#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from source_azure_table.streams import AzureTableStream

from airbyte_cdk.models import AirbyteCatalog, SyncMode


# Tests
def test_discover(mocker, config, tables, source, logger):
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
        "additionalProperties": True,
        "properties": {"PartitionKey": {"type": "string"}},
    }
    assert stream.supported_sync_modes == [SyncMode.full_refresh, SyncMode.incremental]
    assert stream.source_defined_cursor is True
    assert stream.default_cursor_field == ["PartitionKey"]


def test_streams(mocker, config, tables, source, logger):
    mocker.patch(
        "source_azure_table.azure_table.AzureTableReader.get_tables",
        return_value=tables,
    )
    streams = source.streams(logger=logger, config=config)
    assert len(streams) == 2
    assert all(isinstance(stream, AzureTableStream) for stream in streams)
