#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from source_airtable.helpers import Helpers


@pytest.fixture
def base_id():
    return "app1234567890"


@pytest.fixture
def api_key():
    return "key1234567890"


@pytest.fixture
def table():
    return "Table 1"


@pytest.fixture
def auth():
    return MagicMock()


@pytest.fixture
def json_response():
    return {"records": [{"id": "abc", "fields": {"name": "test"}}]}


@pytest.fixture
def expected_json_schema():
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "properties": {
            "_airtable_created_time": {"type": ["null", "string"]},
            "_airtable_id": {"type": ["null", "string"]},
            "name": {"type": ["null", "string"]},
        },
        "type": "object",
    }


def test_get_most_complete_row(auth, base_id, table, json_response):
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = HTTPStatus.OK
        mock_get.return_value.json.return_value = json_response
        assert Helpers.get_most_complete_row(auth, base_id, table) == {"id": "abc", "fields": {"name": "test"}}


def test_get_most_complete_row_invalid_api_key(base_id, table):
    with pytest.raises(Exception):
        auth = TokenAuthenticator("invalid_api_key")
        Helpers.get_most_complete_row(auth, base_id, table)


def test_get_most_complete_row_table_not_found(auth, base_id, table):
    with patch("requests.exceptions.HTTPError") as mock_get:
        mock_get.return_value.status_code = HTTPStatus.NOT_FOUND
        with pytest.raises(Exception):
            Helpers.get_most_complete_row(auth, base_id, table)


def test_get_json_schema(json_response, expected_json_schema):
    json_schema = Helpers.get_json_schema(json_response["records"][0])
    assert json_schema == expected_json_schema


def test_get_airbyte_stream(table, expected_json_schema):
    stream = Helpers.get_airbyte_stream(table, expected_json_schema)
    assert stream
    assert stream.name == table
    assert stream.json_schema == expected_json_schema
