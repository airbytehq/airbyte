#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import date
from unittest.mock import MagicMock

import pytest
from source_kyriba.source import BankBalancesStream

from .test_streams import config


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(BankBalancesStream, "primary_key", "test_primary_key")
    mocker.patch.object(BankBalancesStream, "__abstractmethods__", set())


def test_stream_slices(patch_base_class):
    stream = BankBalancesStream(**config())
    account_uuids = [
        {"account_uuid": "first"},
        {"account_uuid": "second"}
    ]
    stream.get_account_uuids = MagicMock(return_value=account_uuids)
    stream.start_date = date(2022, 1, 1)
    stream.end_date = date(2022, 1, 2)
    expected = [
        {
            "account_uuid": "first",
            "date": "2022-01-01",
        },
        {
            "account_uuid": "second",
            "date": "2022-01-01",
        },
        {
            "account_uuid": "first",
            "date": "2022-01-02",
        },
        {
            "account_uuid": "second",
            "date": "2022-01-02",
        }
    ]
    slices = stream.stream_slices()
    assert slices == expected


def test_path(patch_base_class):
    stream = BankBalancesStream(**config())
    inputs = {"stream_slice": {"account_uuid": "uuid"}}
    path = stream.path(**inputs)
    assert path == "bank-balances/accounts/uuid/balances"


def test_request_params(patch_base_class):
    stream = BankBalancesStream(**config())
    inputs = {
        "stream_slice": {"account_uuid": "uuid", "date": "2022-02-01"},
        "stream_state": {},
    }
    stream.balance_type = "END_OF_DAY"
    params = stream.request_params(**inputs)
    expected = {
        "date": inputs["stream_slice"]["date"],
        "type": stream.balance_type,
    }
    assert params == expected
