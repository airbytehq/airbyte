#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from unittest.mock import MagicMock

import pytest
import requests
from source_google_sheets.client import GoogleSheetsClient


@pytest.mark.parametrize("status, need_give_up", [(429, False), (500, False), (404, True)])
def test_backoff_give_up(status, need_give_up, mocker):
    e = requests.HTTPError("error")
    e.resp = mocker.Mock(status=status)
    assert need_give_up is GoogleSheetsClient.Backoff.give_up(e)


def test_backoff_get_batch_size():
    client = GoogleSheetsClient(
        {"auth_type": "Client", "client_id": "fake_client_id", "client_secret": "fake_client_secret", "refresh_token": "fake_refresh_token"}
    )
    assert client.get_batch_size({"batch_size": 200}) == 200
    row_batch_size = client.get_batch_size({"batch_size": 200})
    assert client._create_range("spreadsheet_id", 0, row_batch_size) == "spreadsheet_id!0:200"
    e = requests.HTTPError("error")
    e.status_code = 429
    assert client.get_batch_size({"batch_size": 200}) == 200
    row_batch_size = client.get_batch_size({"batch_size": 200})
    assert client._create_range("spreadsheet_id", 0, row_batch_size) == "spreadsheet_id!0:200"


def test_client_get_values_on_backoff(caplog):
    client_google_sheets = GoogleSheetsClient(
        {
            "auth_type": "Client",
            "client_id": "fake_client_id",
            "client_secret": "fake_client_secret",
            "refresh_token": "fake_refresh_token",
        },
    )
    row_batch_size = client_google_sheets.get_batch_size({"batch_size": 200})
    client_google_sheets.client.values = MagicMock(return_value=MagicMock(batchGet=MagicMock()))

    assert row_batch_size == 200
    client_google_sheets.get_values(
        sheet="sheet",
        row_cursor=0,
        row_batch_size=row_batch_size,
        spreadsheetId="spreadsheet_id",
        majorDimension="ROWS",
    )

    assert "Fetching range sheet!0:200" in caplog.text
    assert client_google_sheets.get_batch_size({"batch_size": 200}) == 200
    e = requests.HTTPError("error")
    e.status_code = 429
    assert client_google_sheets.get_batch_size({"batch_size": 200}) == 200
    row_batch_size = client_google_sheets.get_batch_size({"batch_size": 200})
    client_google_sheets.get_values(
        sheet="sheet",
        row_cursor=0,
        row_batch_size=row_batch_size,
        spreadsheetId="spreadsheet_id",
        majorDimension="ROWS",
    )

    assert "Fetching range sheet!0:200" in caplog.text
