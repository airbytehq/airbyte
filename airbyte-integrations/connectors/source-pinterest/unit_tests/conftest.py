#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from pytest import fixture


@fixture
def test_config():
    return {
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "refresh_token": "test_refresh_token",
        "window_in_days": "Sandbox",
        "start_date": "2021-05-07",
    }


@fixture
def test_incremental_config():
    return {
        "authenticator": MagicMock(),
        "window_in_days": 185,
        "start_date": "2021-05-07",
    }


@fixture
def test_current_stream_state():
    return {"updated_time": "2021-10-22"}


@fixture
def test_record():
    return {"items": [{}], "bookmark": "string"}


@fixture
def test_record_filter():
    return {"items": [{"updated_time": "2021-11-01"}], "bookmark": "string"}


@fixture
def test_response(test_record):
    response = MagicMock()
    response.json.return_value = test_record
    return response


@fixture
def test_response_filter(test_record_filter):
    response = MagicMock()
    response.json.return_value = test_record_filter
    return response
