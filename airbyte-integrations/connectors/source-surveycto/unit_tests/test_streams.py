#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
from source_surveycto.helpers import Helpers


@pytest.fixture(name='config')
def config_fixture():
    return {'server_name': 'server_name', 'form_id': 'form_id', 'start_date': 'Jan 09, 2022 00:00:00 AM', 'password': 'password', 'username': 'username'}


@pytest.fixture
def form_id():
    return "baseline_ig"


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
        "properties": {'fields': {'name': 'test'}, 'id': 'abc'},
        "type": "object",
    }


def test_get_json_schema(json_response, expected_json_schema):
    json_schema = Helpers.get_json_schema(json_response["records"][0])
    assert json_schema == expected_json_schema
