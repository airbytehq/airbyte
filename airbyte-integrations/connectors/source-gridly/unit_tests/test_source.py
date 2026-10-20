#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_gridly.source import SourceGridly

from airbyte_cdk.models import AirbyteMessage, SyncMode, Type
from airbyte_cdk.models.airbyte_protocol_serializers import AirbyteMessageSerializer
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


CONFIG = {"api_key": "IbuIBdkFjrJps6", "grid_id": "4539o52kmdjmzwp"}
BASE_URL = "https://api.gridly.com/v1"
GRID_URL = f"{BASE_URL}/grids/{CONFIG['grid_id']}"
VIEWS_URL = f"{BASE_URL}/views?gridId={CONFIG['grid_id']}"
RECORDS_URL = f"{BASE_URL}/views/view1/records"
VIEW_RESPONSE = {
    "id": "view1",
    "name": "Default view",
    "columns": [{"id": "_recordId"}, {"id": "column1", "type": "singleLine"}, {"id": "column2", "type": "number"}],
}
VIEWS_RESPONSE = [
    VIEW_RESPONSE,
    {
        "id": "view2",
        "name": "Second view",
        "columns": [{"id": "_recordId"}, {"id": "column1", "type": "singleLine"}, {"id": "column2", "type": "number"}],
    },
]
EXPECTED_JSON_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "properties": {
        "_recordId": {"type": ["null", "string"]},
        "column1": {"type": ["null", "string"]},
        "column2": {"type": ["null", "number"]},
    },
    "type": "object",
}


def test_check_connection(requests_mock):
    source = SourceGridly()
    requests_mock.get(GRID_URL, json={})
    assert source.check_connection(MagicMock(), CONFIG) == (True, None)


def test_streams(requests_mock):
    source = SourceGridly()
    requests_mock.get(VIEWS_URL, json=VIEWS_RESPONSE)
    streams = source.streams(CONFIG)
    expected_streams_number = 2
    assert len(streams) == expected_streams_number


def test_discover(requests_mock):
    requests_mock.get(VIEWS_URL, json=VIEWS_RESPONSE)

    catalog = SourceGridly().discover(MagicMock(), CONFIG)

    stream = catalog.streams[0]
    assert stream.supported_sync_modes == [SyncMode.full_refresh]
    serialized_streams = AirbyteMessageSerializer.dump(AirbyteMessage(type=Type.CATALOG, catalog=catalog))["catalog"]["streams"]
    assert serialized_streams == [
        {"name": "Default view", "json_schema": EXPECTED_JSON_SCHEMA, "supported_sync_modes": ["full_refresh"]},
        {"name": "Second view", "json_schema": EXPECTED_JSON_SCHEMA, "supported_sync_modes": ["full_refresh"]},
    ]


def test_read_records_paginates(requests_mock):
    requests_mock.get(VIEWS_URL, json=VIEWS_RESPONSE)
    first_page = [
        {"id": f"record-{index}", "cells": [{"columnId": "column1", "value": f"value-{index}"}, {"columnId": "column2", "value": index}]}
        for index in range(100)
    ]
    second_page = [
        {
            "id": f"record-{index}",
            "cells": [{"columnId": "column1", "value": f"value-{index}"}, {"columnId": "column2", "value": index}],
        }
        for index in range(100, 150)
    ]
    requests_mock.get(
        RECORDS_URL,
        response_list=[
            {"json": first_page, "headers": {"x-total-count": "150"}},
            {"json": second_page, "headers": {"x-total-count": "150"}},
        ],
    )
    catalog = CatalogBuilder().with_stream("Default view", SyncMode.full_refresh).build()

    output = read(SourceGridly(), CONFIG, catalog)

    assert output.errors == [], output.get_formatted_error_message()
    assert len(output.records) == 150
    assert output.records[0].record.data == {"_recordId": "record-0", "column1": "value-0", "column2": 0}
    records_requests = [request for request in requests_mock.request_history if request.url.startswith(RECORDS_URL)]
    assert len(records_requests) == 2
    assert records_requests[0].qs == {}
    assert records_requests[1].qs == {"page": ['{"offset":100,"limit":100}']}
