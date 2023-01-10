#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import pytest
from airbyte_cdk.models import AirbyteStream
from airbyte_cdk.models.airbyte_protocol import DestinationSyncMode, SyncMode
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator


@pytest.fixture
def config():
    return {
        "api_key": "key1234567890",
    }


@pytest.fixture
def fake_auth():
    return TokenAuthenticator(token="key1234567890")


@pytest.fixture
def fake_bases_response():
    return {"bases": [{"id": 1234, "name": "test_base"}]}


@pytest.fixture
def expected_bases_response():
    return [{"id": 1234, "name": "test_base"}]


@pytest.fixture
def fake_tables_response():
    return {"tables": [{"id": 5678, "name": "test_table"}]}


@pytest.fixture
def expected_discovery_stream_name():
    return ["test_base/test_table"]


@pytest.fixture
def field_name_to_cleaned():
    return "The Name (That should be cleaned)"


@pytest.fixture
def expected_clean_name():
    return "the_name_(that_should_be_cleaned)"


@pytest.fixture
def table():
    return "Table 1"


@pytest.fixture
def json_response():
    return {
        "records": [
            {
                "id": "abc",
                "fields": [
                    {
                        'type': 'singleLineText',
                        'id': '_fake_id_',
                        'name': 'test',
                    }
                ]
            }
        ]
    }


@pytest.fixture
def streams_json_response():
    return {
        "records": [
            {
                'id': 'some_id',
                'createdTime': '2022-12-02T19:50:00.000Z',
                'fields': {'field1': True, 'field2': "test", 'field3': 123},
            }
        ]
    }


@pytest.fixture
def streams_processed_response():
    return [
        {
            '_airtable_id': 'some_id',
            '_airtable_created_time': '2022-12-02T19:50:00.000Z',
            'field1': True,
            'field2': 'test',
            'field3': 123,
        }
    ]


@pytest.fixture
def expected_json_schema():
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "additionalProperties": True,
        "properties": {
            "_airtable_created_time": {"type": ["null", "string"]},
            "_airtable_id": {"type": ["null", "string"]},
            "test": {"type": ["null", "string"]},
        },
        "type": "object",
    }


@pytest.fixture(scope='function', autouse=True)
def prepared_stream():
    return {
        "stream_path": "some_base_id/some_table_id",
        "stream": AirbyteStream(
            name="test_base/test_table",
            json_schema={
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "additionalProperties": True,
                "properties": {
                    "_airtable_id": {
                        "type": [
                            "null",
                            "string"
                        ]
                    },
                    "_airtable_created_time": {
                        "type": [
                            "null",
                            "string"
                        ]
                    },
                    "name": {
                        "type": [
                            "null",
                            "string"
                        ]
                    }
                }
            },
            supported_sync_modes=[SyncMode.full_refresh],
            supported_destination_sync_modes=[DestinationSyncMode.overwrite, DestinationSyncMode.append_dedup],
        )
    }
