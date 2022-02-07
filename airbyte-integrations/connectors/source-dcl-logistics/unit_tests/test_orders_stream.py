#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
from source_dcl_logistics.source import Orders


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(Orders, "path", "v0/example_endpoint")
    mocker.patch.object(Orders, "primary_key", "test_primary_key")
    mocker.patch.object(Orders, "__abstractmethods__", set())


def test_request_params(patch_base_class):
    stream = Orders()
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": {"page": 1}}
    expected_params = {"extended_date": True, "page": 1, "page_size": 100}
    assert stream.request_params(**inputs) == expected_params


def test_parse_response(patch_base_class):
    stream = Orders()
    fake_order_dict = {"order_number": 1}
    fake_json_response = {"orders": [fake_order_dict]}
    inputs = {"response": MagicMock(json=MagicMock(return_value=fake_json_response))}
    expected_parsed_object = fake_order_dict
    assert list(stream.parse_response(**inputs)) == [expected_parsed_object]


def test_has_more_pages(patch_base_class):
    stream = Orders()
    fake_json_response = {"orders": None}
    inputs = {"response": MagicMock(json=MagicMock(return_value=fake_json_response))}
    list(stream.parse_response(**inputs))
    assert not stream.has_more_pages
