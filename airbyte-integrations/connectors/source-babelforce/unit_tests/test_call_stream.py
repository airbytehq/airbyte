#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from datetime import datetime
from unittest.mock import MagicMock

import pytest
from source_babelforce.source import Calls, InvalidStartAndEndDateException


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(Calls, "path", "v0/example_endpoint")
    mocker.patch.object(Calls, "primary_key", "test_primary_key")
    mocker.patch.object(Calls, "__abstractmethods__", set())


def test_request_params(patch_base_class):
    stream = Calls(region="services")
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": {"page": 1}}
    expected_params = {"max": 100, "page": 1}
    assert stream.request_params(**inputs) == expected_params


def test_date_created_from_less_than_date_created_to_not_raise_exception(patch_base_class):
    try:
        stream = Calls(region="services", date_created_from=1, date_created_to=2)
        inputs = {"stream_slice": None, "stream_state": None, "next_page_token": {"page": 1}}
        stream.request_params(**inputs)
    except InvalidStartAndEndDateException as exception:
        assert False, exception


def test_date_created_from_less_than_date_created_to_raise_exception(patch_base_class):
    with pytest.raises(InvalidStartAndEndDateException):
        stream = Calls(region="services", date_created_from=2, date_created_to=1)
        inputs = {"stream_slice": None, "stream_state": None, "next_page_token": {"page": 1}}
        stream.request_params(**inputs)


def test_parse_response(patch_base_class):
    stream = Calls(region="services")

    fake_date_str = "2022-04-27T00:00:00"
    fake_date = datetime.strptime(fake_date_str, "%Y-%m-%dT%H:%M:%S")

    fake_item = {
        "id": "abc",
        "parentId": "abc",
        "sessionId": "abc",
        "conversationId": "abc",
        "dateCreated": fake_date,
        "dateEstablished": None,
        "dateFinished": fake_date,
        "lastUpdated": fake_date,
        "state": "completed",
        "finishReason": "unreachable",
        "from": "123",
        "to": "123",
        "type": "outbound",
        "source": "queue",
        "domain": "internal",
        "duration": 0,
        "anonymous": False,
        "recordings": [],
        "bridged": {}
    }

    fake_call_json = {
        "items": [fake_item]
    }
    inputs = {"response": MagicMock(json=MagicMock(return_value=fake_call_json))}
    assert next(stream.parse_response(**inputs)) == fake_item
