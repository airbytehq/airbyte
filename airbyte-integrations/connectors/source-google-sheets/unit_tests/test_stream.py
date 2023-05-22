#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
import requests
from airbyte_cdk.utils import AirbyteTracedException
from apiclient import errors
from source_google_sheets import SourceGoogleSheets
from source_google_sheets.client import GoogleSheetsClient
from source_google_sheets.helpers import SCOPES


def test_invalid_credentials_error_message(invalid_config):
    source = SourceGoogleSheets()
    with pytest.raises(AirbyteTracedException) as e:
        source.check(logger=None, config=invalid_config)
    assert e.value.args[0] == 'Access to the spreadsheet expired or was revoked. Re-authenticate to restore access.'


def test_invalid_link_error_message(mocker, invalid_config):
    source = SourceGoogleSheets()
    resp = requests.Response()
    resp.status = 404
    mocker.patch.object(GoogleSheetsClient, "__init__", lambda s, credentials, scopes=SCOPES: None)
    mocker.patch.object(GoogleSheetsClient, "get", side_effect=errors.HttpError(resp=resp, content=b''))
    with pytest.raises(AirbyteTracedException) as e:
        source.check(logger=None, config=invalid_config)
    expected_message = 'Config error: The spreadsheet link is not valid. Enter the URL of the Google spreadsheet you want to sync.'
    assert e.value.args[0] == expected_message
