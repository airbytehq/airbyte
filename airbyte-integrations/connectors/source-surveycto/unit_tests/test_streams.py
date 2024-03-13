#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import base64
from unittest.mock import MagicMock

import pendulum
import pytest
from source_surveycto.helpers import Helpers


@pytest.fixture(name="config")
def config_fixture():
    return {
        "server_name": "server_name",
        "form_id": "form_id",
        "start_date": "Jan 09, 2022 00:00:00 AM",
        "password": "password",
        "username": "username",
        "dataset_id": "dataset",
    }


@pytest.fixture
def form_id():
    return "form_id"


@pytest.fixture
def auth():
    return MagicMock()


@pytest.fixture
def json_response():
    return {"records": [{"id": "abc", "fields": {"name": "test"}}]}


@pytest.fixture
def expected_json_schema():
    return (
        {
            "type": "object",
            "properties": {
                "id": {"type": "string", "additionalProperties": True},
                "fields": {
                    "additionalProperties": True,
                    "type": "object",
                    "properties": {"name": {"type": "string", "additionalProperties": True}},
                },
            },
            "additionalProperties": True,
        },
    )


def test_get_json_schema(json_response, expected_json_schema):
    schema = Helpers.get_filter_data(json_response["records"][0])
    assert schema == expected_json_schema[0]


def test_base64_encode():
    assert Helpers._base64_encode("test") == "dGVzdA=="


def test_format_date():
    date = pendulum.parse("Jan 09, 2022 12:00:00 AM", strict=False).isoformat()
    assert Helpers.format_date(date) == "Jan 09, 2022 12:00:00 AM"
