#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.models import AirbyteCatalog, AirbyteConnectionStatus, AirbyteStream, Status, SyncMode
from source_dynamodb import reader, source


def test_check(
    populate_table,
    mock_logger,
    credentials,
    my_source: source.SourceDynamodb,
):
    connection_status = my_source.check(logger=mock_logger, config=credentials)
    assert connection_status == AirbyteConnectionStatus(status=Status.SUCCEEDED, message=None)


def test_discover(
    populate_table,
    mock_logger,
    credentials,
    my_source: source.SourceDynamodb,
    my_reader: reader.Reader,
):
    streams = my_source.discover(logger=mock_logger, config=credentials)
    assert streams == AirbyteCatalog(
        streams=[
            AirbyteStream(
                name="Devices",
                json_schema=my_reader.typed_schema,
                source_defined_cursor=None,
                default_cursor_field=None,
                source_defined_primary_key=None,
                namespace=None,
                supported_sync_modes=[SyncMode.full_refresh],
            ),
            AirbyteStream(
                name="Music",
                json_schema=my_reader.typed_schema,
                source_defined_cursor=None,
                default_cursor_field=None,
                source_defined_primary_key=None,
                namespace=None,
                supported_sync_modes=[SyncMode.full_refresh],
            ),
        ]
    )
