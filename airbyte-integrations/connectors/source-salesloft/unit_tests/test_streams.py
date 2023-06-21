#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
from source_salesloft.source import Accounts, SourceSalesloft, Users


def test_request_params(config):
    stream = Users(authenticator=MagicMock(), start_date=config["start_date"])
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {"page": 1, "per_page": 100}
    assert stream.request_params(**inputs) == expected_params


def test_incremental_request_params(config):
    stream = Accounts(authenticator=MagicMock(), start_date=config["start_date"])
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {
        "page": 1,
        "per_page": 100,
        "created_at[gt]": "2020-01-01T00:00:00.000000Z",
        "updated_at[gt]": "2020-01-01T00:00:00.000000Z"
    }
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token(config):
    stream = Users(authenticator=MagicMock(), start_date=config["start_date"])
    response = MagicMock(json=MagicMock(return_value={"metadata": {"paging": {"next_page": 2}}}))
    inputs = {"response": response}
    expected_token = {"page": 2}
    assert stream.next_page_token(**inputs) == expected_token


def test_next_page_token_invalid(config):
    stream = Users(authenticator=MagicMock(), start_date=config["start_date"])
    response = MagicMock(json=MagicMock(return_value={"metadata": {"paginfffg": {"next_pagaae": 2}}}))
    inputs = {"response": response}
    with pytest.raises(KeyError) as ex:
        stream.next_page_token(inputs)
    assert isinstance(ex.value, KeyError)


def test_get_updated_state():
    stream = Accounts(authenticator=MagicMock(), start_date="2021-09-21T00:00:00.504817-04:00")
    inputs = {"current_stream_state": {}, "latest_record": {}}
    expected_state = {"updated_at": "2021-09-21T04:00:00.504817Z"}
    assert stream.get_updated_state(**inputs) == expected_state


@pytest.mark.parametrize(
    "return_value, expected_records",
    (
        ({}, []),
        ({"data": [{"id": 1}, {"id": 2}]}, [{"id": 1}, {"id": 2}])
    )
)
def test_parse_response(config, return_value, expected_records):
    stream = Users(authenticator=MagicMock(), start_date=config["start_date"])
    response = MagicMock(json=MagicMock(return_value=return_value))
    assert list(stream.parse_response(response)) == expected_records


def test_stream_has_path(config):
    for stream in SourceSalesloft().streams(config):
        assert stream.path()
