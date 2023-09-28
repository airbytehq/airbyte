#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
import requests
from source_google_sheets.client import GoogleSheetsClient


@pytest.mark.parametrize(
    "status, need_give_up",
    [
        (429, False), (500, False), (404, True)
    ]
)
def test_backoff_give_up(status, need_give_up, mocker):
    e = requests.HTTPError('error')
    e.resp = mocker.Mock(status=status)
    assert need_give_up is GoogleSheetsClient.Backoff.give_up(e)


def test_backoff_increase_row_batch_size(mocker):
    assert GoogleSheetsClient.Backoff.row_batch_size == 200
    e = requests.HTTPError('error')
    e.status_code = 429
    GoogleSheetsClient.Backoff.increase_row_batch_size({"exception": e})
    assert GoogleSheetsClient.Backoff.row_batch_size == 210
    GoogleSheetsClient.Backoff.row_batch_size = 1000
    GoogleSheetsClient.Backoff.increase_row_batch_size({"exception": e})
    assert GoogleSheetsClient.Backoff.row_batch_size == 1000
