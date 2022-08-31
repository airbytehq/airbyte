#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
import requests
from source_kyriba.source import Accounts, AccountSubStream

from .test_streams import config


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(AccountSubStream, "path", "v0/example_endpoint")
    mocker.patch.object(AccountSubStream, "primary_key", "test_primary_key")
    mocker.patch.object(AccountSubStream, "__abstractmethods__", set())


def test_get_account_uuids(patch_base_class):
    stream = AccountSubStream(**config())
    account_records = [{"uuid": "first"}, {"uuid": "second"}]
    Accounts.read_records = MagicMock(return_value=account_records)
    expected = [{"account_uuid": "first"}, {"account_uuid": "second"}]
    assert stream.get_account_uuids() == expected


def test_parse_response(patch_base_class):
    stream = AccountSubStream(**config())
    resp = requests.Response()
    resp_dict = {"uuid": "uuid"}
    resp.json = MagicMock(return_value=resp_dict)
    inputs = {"response": resp}
    expected = {"uuid": "uuid"}
    assert next(stream.parse_response(**inputs)) == expected
