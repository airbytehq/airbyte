#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import pytest
from source_google_sheets.utils import exception_description_by_status_code, name_conversion, safe_name_conversion


def test_name_conversion():
    assert name_conversion("My_Name") == "my_name"
    assert name_conversion("My Name") == "my_name"
    assert name_conversion("MyName") == "my_name"
    assert name_conversion("mYName") == "m_yname"
    assert name_conversion("MyName123") == "my_name_123"
    assert name_conversion("My123name") == "my_123_name"
    assert name_conversion("My_Name!") == "my_name_"
    assert name_conversion("My_Name____c") == "my_name_c"
    assert name_conversion("1MyName") == "_1_my_name"
    assert name_conversion("!MyName") == "_my_name"
    assert name_conversion("прівит світ") == "privit_svit"


def test_safe_name_conversion():
    with pytest.raises(Exception) as exc_info:
        safe_name_conversion("*****")
    assert exc_info.value.args[0] == "initial string '*****' converted to empty"


@pytest.mark.parametrize(
    "status_code, expected_message",
    [
        (
            404,
            "The requested Google Sheets spreadsheet with id spreadsheet_id does not exist. Please ensure the Spreadsheet Link you have set is valid and the spreadsheet exists. If the issue persists, contact support",
        ),
        (429, "Rate limit has been reached. Please try later or request a higher quota for your account."),
        (
            500,
            "There was an issue with the Google Sheets API. This is usually a temporary issue from Google's side. Please try again. If this issue persists, contact support",
        ),
        (
            403,
            "The authenticated Google Sheets user does not have permissions to view the spreadsheet with id spreadsheet_id. Please ensure the authenticated user has access to the Spreadsheet and reauthenticate. If the issue persists, contact support",
        ),
    ],
)
def test_exception_description_by_status_code(status_code, expected_message):
    assert expected_message == exception_description_by_status_code(status_code, "spreadsheet_id")
