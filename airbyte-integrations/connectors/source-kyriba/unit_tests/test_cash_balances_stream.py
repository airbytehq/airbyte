#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from datetime import date
from unittest.mock import MagicMock

import pytest
from source_kyriba.source import CashBalancesStream

from .test_streams import config


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(CashBalancesStream, "primary_key", "test_primary_key")
    mocker.patch.object(CashBalancesStream, "__abstractmethods__", set())


def test_stream_slices(patch_base_class):
    stream = CashBalancesStream(**config())
    account_uuids = [{"account_uuid": "first"}, {"account_uuid": "second"}]
    stream.get_account_uuids = MagicMock(return_value=account_uuids)
    stream.start_date = date(2022, 1, 1)
    stream.end_date = date(2022, 3, 1)
    expected = [
        {
            "account_uuid": "first",
            "startDate": "2022-01-01",
            "endDate": "2022-02-01",
        },
        {
            "account_uuid": "second",
            "startDate": "2022-01-01",
            "endDate": "2022-02-01",
        },
        {
            "account_uuid": "first",
            "startDate": "2022-02-02",
            "endDate": "2022-03-01",
        },
        {
            "account_uuid": "second",
            "startDate": "2022-02-02",
            "endDate": "2022-03-01",
        },
    ]
    slices = stream.stream_slices()
    assert slices == expected


def test_path(patch_base_class):
    stream = CashBalancesStream(**config())
    inputs = {"stream_slice": {"account_uuid": "uuid"}}
    path = stream.path(**inputs)
    assert path == "cash-balances/accounts/uuid/balances"


def test_request_params(patch_base_class):
    stream = CashBalancesStream(**config())
    inputs = {
        "stream_slice": {"account_uuid": "uuid", "startDate": "2022-01-01", "endDate": "2022-02-01"},
        "stream_state": {},
    }
    stream.intraday = False
    params = stream.request_params(**inputs)
    expected = {
        "startDate": "2022-01-01",
        "endDate": "2022-02-01",
        "intraday": False,
        "actual": True,
        "estimatedForecasts": False,
        "confirmedForecasts": False,
        "dateType": "VALUE",
    }
    assert params == expected
