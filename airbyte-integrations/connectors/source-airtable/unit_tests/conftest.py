#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import pytest
from source_airtable.streams import AirtableStream

from airbyte_cdk.models import AirbyteStream, ConfiguredAirbyteCatalog
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
    return ["test_base/test_table/5678"]


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
                        "type": "singleLineText",
                        "id": "_fake_id_",
                        "name": "test",
                    }
                ],
            }
        ]
    }


@pytest.fixture
def streams_json_response():
    return {
        "records": [
            {
                "id": "some_id",
                "createdTime": "2022-12-02T19:50:00.000Z",
                "fields": {"field1": True, "field2": "test", "field3": 123},
            }
        ]
    }


@pytest.fixture
def streams_processed_response(table):
    return [
        {
            "_airtable_id": "some_id",
            "_airtable_created_time": "2022-12-02T19:50:00.000Z",
            "_airtable_table_name": table,
            "field1": True,
            "field2": "test",
            "field3": 123,
        }
    ]


@pytest.fixture
def expected_json_schema():
    return {
        "$schema": "https://json-schema.org/draft-07/schema#",
        "additionalProperties": True,
        "properties": {
            "_airtable_created_time": {"type": ["null", "string"]},
            "_airtable_id": {"type": ["null", "string"]},
            "_airtable_table_name": {"type": ["null", "string"]},
            "test": {"type": ["null", "string"]},
        },
        "type": "object",
    }


@pytest.fixture(scope="function", autouse=True)
def prepared_stream(table):
    return {
        "stream_path": "some_base_id/some_table_id",
        "stream": AirbyteStream(
            name="test_base/test_table",
            json_schema={
                "$schema": "https://json-schema.org/draft-07/schema#",
                "type": "object",
                "additionalProperties": True,
                "properties": {
                    "_airtable_id": {"type": ["null", "string"]},
                    "_airtable_created_time": {"type": ["null", "string"]},
                    "_airtable_table_name": {"type": ["null", "string"]},
                    "name": {"type": ["null", "string"]},
                },
            },
            supported_sync_modes=[SyncMode.full_refresh],
            supported_destination_sync_modes=[DestinationSyncMode.overwrite, DestinationSyncMode.append_dedup],
        ),
        "table_name": table,
    }


@pytest.fixture
def make_airtable_stream(prepared_stream):
    def make(name):
        return AirtableStream(
            stream_path=prepared_stream["stream_path"],
            stream_name=name,
            stream_schema=prepared_stream["stream"].json_schema,
            table_name=prepared_stream["table_name"],
            authenticator=fake_auth,
        )

    return make


@pytest.fixture
def make_stream(prepared_stream):
    def make(name):
        return {
            "stream_path": prepared_stream["stream_path"],
            "stream": AirbyteStream(
                name=name,
                json_schema=prepared_stream["stream"].json_schema,
                supported_sync_modes=[SyncMode.full_refresh],
                supported_destination_sync_modes=[DestinationSyncMode.overwrite, DestinationSyncMode.append_dedup],
            ),
            "sync_mode": SyncMode.full_refresh,
            "destination_sync_mode": DestinationSyncMode.overwrite,
        }

    return make


@pytest.fixture
def fake_catalog(make_stream):
    stream1 = make_stream(name="test_base/test_table1/abcdef")
    stream2 = make_stream(name="test_base/test_table2/qwerty")
    return ConfiguredAirbyteCatalog(
        streams=[stream1, stream2],
    )


@pytest.fixture
def fake_streams(make_airtable_stream):
    stream1 = make_airtable_stream(name="test_base/test_table1/abcdef")
    stream2 = make_airtable_stream(name="test_base/test_table2_renamed/qwerty")
    yield [stream1, stream2]
