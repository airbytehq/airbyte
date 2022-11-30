#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from source_chartmogul.source import Activities, Customers


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(Customers, "__abstractmethods__", set())
    mocker.patch.object(Activities, "__abstractmethods__", set())


class TestCustomers:
    def test_request_params(self):
        stream = Customers()
        inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
        expected_params = {"page": 1}
        assert stream.request_params(**inputs) == expected_params

        next_page_token = {"page": 3}
        inputs = {"stream_slice": None, "stream_state": None, "next_page_token": next_page_token}
        expected_params = {"page": 3}
        assert stream.request_params(**inputs) == expected_params

    def test_next_page_token(self, mocker):
        stream = Customers()
        response = mocker.MagicMock()

        # no more results
        response.json.return_value = {"has_more": False}
        inputs = {"response": response}
        assert stream.next_page_token(**inputs) is None

        # there is more results
        response.json.return_value = {"has_more": True, "current_page": 42}
        inputs = {"response": response}
        assert stream.next_page_token(**inputs) == {"page": 43}

    def test_parse_response(self, mocker):
        stream = Customers()
        response = mocker.MagicMock()
        response.json.return_value = {"entries": [{"one": 1}, {"two": 2}]}
        inputs = {"response": response}
        expected_parsed_object = {"one": 1}
        assert next(stream.parse_response(**inputs)) == expected_parsed_object


# Activites stream tests


class TestActivities:
    def test_request_params(self):
        # no start_date set
        stream = Activities(start_date=None)
        inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
        assert stream.request_params(**inputs) == {}

        # start_date is set
        stream.start_date = "2010-01-01"
        inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
        assert stream.request_params(**inputs) == {"start-date": stream.start_date}

        # start-after is available
        next_page_token = {"start-after": "a-b-c"}
        inputs = {"stream_slice": None, "stream_state": None, "next_page_token": next_page_token}
        expected_params = next_page_token
        assert stream.request_params(**inputs) == expected_params

    def test_next_page_token(self, mocker):
        stream = Activities(start_date=None)
        response = mocker.MagicMock()

        # no more results
        response.json.return_value = {"has_more": False}
        inputs = {"response": response}
        assert stream.next_page_token(**inputs) is None

        # there is more results
        response.json.return_value = {"has_more": True, "entries": [{"uuid": "unique-uuid"}]}
        inputs = {"response": response}
        assert stream.next_page_token(**inputs) == {"start-after": "unique-uuid"}
