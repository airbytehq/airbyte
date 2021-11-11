#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import patch

import pytest
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from source_airtable.helpers import Helpers


def test_get_first_row(auth, base_id, table, json_response):
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = HTTPStatus.OK
        mock_get.return_value.json.return_value = json_response
        assert Helpers.get_first_row(auth, base_id, table) == {"id": "abc", "fields": {"name": "test"}}


def test_invalid_api_key(base_id, table):
    with pytest.raises(Exception):
        auth = TokenAuthenticator("invalid_api_key")
        Helpers.get_first_row(auth, base_id, table)


def test_table_not_found(auth, base_id, table):
    with patch("requests.exceptions.HTTPError") as mock_get:
        mock_get.return_value.status_code = HTTPStatus.NOT_FOUND
        with pytest.raises(Exception):
            Helpers.get_first_row(auth, base_id, table)


def test_gest_json_schema(json_response, expected_json_schema):
    json_schema = Helpers.get_json_schema(json_response["records"][0])
    assert json_schema == expected_json_schema


def test_get_airbyte_stream(table, expected_json_schema):
    Helpers.get_airbyte_stream(table, expected_json_schema)
