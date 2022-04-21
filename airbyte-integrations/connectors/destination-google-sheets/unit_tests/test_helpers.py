#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from destination_google_sheets.helpers import get_spreadsheet_id
    
TEST_CONFIG: dict = {
    "spreadsheet_id": "https://docs.google.com/spreadsheets/d/185wXuD532Anfj9ivNH8TQKZK8wVYfDu21U-nGJjdFXw/edit#gid=0",
    "credentials": {
        "auth_type": "Client",
        "client_id": "CLIENT_ID",
        "client_secret": "CLIENT_SECRET",
        "refresh_token": "REFRESH_TOKEN"
    }
}

def test_connection_test_write():
    """ TEST FOR TEST CONNECTION"""
    pass
    
def test_get_spreadsheet_id(config: dict = TEST_CONFIG):
    expected = "185wXuD532Anfj9ivNH8TQKZK8wVYfDu21U-nGJjdFXw"
    spreadsheet_id = get_spreadsheet_id(config.get("spreadsheet_id"))
    assert spreadsheet_id == expected
