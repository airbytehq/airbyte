#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest


@pytest.fixture
def test_config():
    return {"api_key": "key1234567890", "base_id": "app1234567890", "tables": ["Imported table", "Table 2"]}


@pytest.fixture
def base_id():
    return "app1234567890"


@pytest.fixture
def api_key():
    return "key1234567890"


@pytest.fixture
def table():
    return "Imported table"


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
