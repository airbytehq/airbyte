#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from datetime import date
from unittest.mock import MagicMock

import requests
from airbyte_cdk.models import SyncMode
from pytest import fixture
from source_kyriba.source import CashFlows

from .test_streams import config


@fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(CashFlows, "primary_key", "test_primary_key")
    mocker.patch.object(CashFlows, "__abstractmethods__", set())


def test_path(patch_base_class):
    stream = CashFlows(**config())
    assert stream.path() == "cash-flows"


def test_stream_slices_new(patch_base_class):
    stream = CashFlows(**config())
    stream.start_date = date(2021, 1, 1)
    stream.end_date = date(2021, 1, 3)
    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": [], "stream_state": {}}
    expected_stream_slice = [
        {
            "startDate": "2021-01-01",
            "endDate": "2021-01-01",
        },
        {
            "startDate": "2021-01-02",
            "endDate": "2021-01-02",
        },
        {
            "startDate": "2021-01-03",
            "endDate": "2021-01-03",
        },
    ]
    assert stream.stream_slices(**inputs) == expected_stream_slice


def test_stream_slices_state(patch_base_class):
    stream = CashFlows(**config())
    stream.start_date = date.fromisoformat("2021-01-01")
    stream.end_date = date.fromisoformat("2021-01-03")
    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": [], "stream_state": {"updateDateTime": "2021-01-02T00:00:00Z"}}
    expected_stream_slice = [
        {
            "startDate": "2021-01-02",
            "endDate": "2021-01-02",
        },
        {
            "startDate": "2021-01-03",
            "endDate": "2021-01-03",
        },
    ]
    assert stream.stream_slices(**inputs) == expected_stream_slice


def test_all_request_params(patch_base_class):
    stream = CashFlows(**config())
    inputs = {
        "stream_state": {
            "updateDateTime": "2022-01-01T00:00:00Z",
        },
        "stream_slice": {
            "startDate": "2021-01-01",
            "endDate": "2022-01-02",
        },
        "next_page_token": {
            "page.offset": 1000,
        },
    }
    expected = {
        "sort": "updateDateTime",
        "page.offset": 1000,
        "filter": "updateDateTime=gt='2022-01-01T00:00:00Z'",
        "dateType": "UPDATE",
        "page.limit": 1000,
        "startDate": "2021-01-01",
        "endDate": "2022-01-02",
    }
    assert stream.request_params(**inputs) == expected


def test_parse_response(patch_base_class):
    stream = CashFlows(**config())
    resp = requests.Response()
    resp_data = {"results": [{"date": {"updateDateTime": "2022-03-01T00:00:00Z"}}]}
    resp.json = MagicMock(return_value=resp_data)
    assert next(stream.parse_response(resp)) == {"updateDateTime": "2022-03-01T00:00:00Z"}
