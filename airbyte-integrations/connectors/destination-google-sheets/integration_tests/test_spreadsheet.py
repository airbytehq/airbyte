#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from destination_google_sheets.client import GoogleSheetsClient
from destination_google_sheets.helpers import get_spreadsheet_id
from destination_google_sheets.spreadsheet import GoogleSheets
from integration_tests.test_helpers import TEST_CONFIG
from pygsheets.client import Client as pygsheets_client


# ----- PREPARE ENV -----


# client instance
TEST_CLIENT: pygsheets_client = GoogleSheetsClient(TEST_CONFIG).authorize()
# get test spreadsheet_id
TEST_SPREADSHEET_ID: str = get_spreadsheet_id(TEST_CONFIG.get("spreadsheet_id"))
# define test Spreadsheet class
TEST_SPREADSHEET: GoogleSheets = GoogleSheets(TEST_CLIENT, TEST_SPREADSHEET_ID)
# define test stream
TEST_STREAM: str = "test_stream"


# ----- BEGIN TESTS -----


def test_spreadsheet():
    assert len(TEST_SPREADSHEET.spreadsheet.worksheets()) > 0


def test_open_worksheet():
    test_wks = TEST_SPREADSHEET.open_worksheet(TEST_STREAM)
    assert test_wks.id is not None


def test_clean_worksheet():
    TEST_SPREADSHEET.clean_worksheet(TEST_STREAM)
    test_wks = TEST_SPREADSHEET.open_worksheet(TEST_STREAM)
    records = test_wks.get_all_records()
    assert len(records) == 0


def test_set_headers():
    test_headers = ["id", "key"]
    TEST_SPREADSHEET.set_headers("test_stream", ["id", "key"])
    test_wks = TEST_SPREADSHEET.open_worksheet(TEST_STREAM)
    headers = test_wks[1]
    for header in test_headers:
        if header in headers:
            assert True


def test_index_cols():
    expected = {"id": 1, "key": 2, "": 26}
    test_wks = TEST_SPREADSHEET.open_worksheet(TEST_STREAM)
    col_indexed = TEST_SPREADSHEET.index_cols(test_wks)
    assert col_indexed == expected


def test_find_duplicates():
    input_values = [[1, "a"], [1, "a"], [2, "b"], [1, "a"], [1, "a"]]
    expected = [6, 5, 3]  # the 4th row is the duplicate of the 1st.

    test_wks = TEST_SPREADSHEET.open_worksheet(TEST_STREAM)
    test_wks.append_table(input_values, start="A2", dimension="ROWS")
    test = TEST_SPREADSHEET.find_duplicates(test_wks, "id")
    assert test == expected


def test_remove_duplicates():
    expected = [{"id": 1, "key": "a"}, {"id": 2, "key": "b"}]
    test_wks = TEST_SPREADSHEET.open_worksheet(TEST_STREAM)
    # find the duplicated rows
    rows_to_remove = TEST_SPREADSHEET.find_duplicates(test_wks, "id")
    # remove duplicates
    TEST_SPREADSHEET.remove_duplicates(test_wks, rows_to_remove)
    records = test_wks.get_all_records()
    assert records == expected


def test_delete_test_stream():
    test_wks = TEST_SPREADSHEET.open_worksheet(TEST_STREAM)
    TEST_SPREADSHEET.spreadsheet.del_worksheet(test_wks)


# ----- END TESTS -----
