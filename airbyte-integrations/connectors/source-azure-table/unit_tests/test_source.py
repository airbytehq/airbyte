#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from source_azure_table.streams import AzureTableStream

from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
    Type,
)
from airbyte_cdk.test.state_builder import StateBuilder


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


def test_stream_json_schema_matches_discover(mocker, source):
    stream = AzureTableStream(stream_name="AzureTable1", reader=mocker.Mock())

    assert stream.get_json_schema() == source.get_typed_schema


def test_read_full_refresh(mocker, config, tables, source, logger):
    mocker.patch("source_azure_table.azure_table.AzureTableReader.get_tables", return_value=tables)
    mocker.patch("source_azure_table.azure_table.AzureTableReader.get_table_client", return_value=mocker.Mock())
    rows = [{"PartitionKey": "1", "RowKey": "a"}, {"PartitionKey": "2", "RowKey": "b"}]
    read_table = mocker.patch("source_azure_table.azure_table.AzureTableReader.read_table", return_value=iter(rows))
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name="AzureTable1",
                    json_schema=source.get_typed_schema,
                    supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental],
                    source_defined_cursor=True,
                    default_cursor_field=["PartitionKey"],
                ),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.append,
                cursor_field=[],
            )
        ]
    )

    messages = list(source.read(logger, config, catalog, state=[]))
    records = [message.record for message in messages if message.type == Type.RECORD]

    assert [record.data for record in records] == rows
    assert [record.stream for record in records] == ["AzureTable1", "AzureTable1"]
    read_table.assert_called_once()
    assert read_table.call_args.kwargs["filter_query"] is None


def test_read_incremental_uses_and_emits_state(mocker, config, tables, source, logger):
    mocker.patch("source_azure_table.azure_table.AzureTableReader.get_tables", return_value=tables)
    mocker.patch("source_azure_table.azure_table.AzureTableReader.get_table_client", return_value=mocker.Mock())
    rows = [{"PartitionKey": "2", "RowKey": "b"}, {"PartitionKey": "3", "RowKey": "c"}]
    read_table = mocker.patch("source_azure_table.azure_table.AzureTableReader.read_table", return_value=iter(rows))
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name="AzureTable1",
                    json_schema=source.get_typed_schema,
                    supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental],
                    source_defined_cursor=True,
                    default_cursor_field=["PartitionKey"],
                ),
                sync_mode=SyncMode.incremental,
                destination_sync_mode=DestinationSyncMode.append,
                cursor_field=["PartitionKey"],
            )
        ]
    )
    state = StateBuilder().with_stream_state("AzureTable1", {"PartitionKey": "1"}).build()

    messages = list(source.read(logger, config, catalog, state=state))
    records = [message.record for message in messages if message.type == Type.RECORD]
    state_messages = [message for message in messages if message.type == Type.STATE]

    assert [record.data for record in records] == rows
    assert state_messages[-1].state.stream.stream_state.__dict__ == {"PartitionKey": "3"}
    read_table.assert_called_once()
    assert read_table.call_args.kwargs["filter_query"] == "PartitionKey gt '1'"
