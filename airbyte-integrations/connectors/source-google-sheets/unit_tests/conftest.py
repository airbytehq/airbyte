#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest


@pytest.fixture
def invalid_config():
    return {
        "spreadsheet_id": "invalid_spreadsheet_id",
        "credentials":
            {
                "auth_type": "Client",
                "client_id": "fake_client_id",
                "client_secret": "fake_client_secret",
                "refresh_token": "fake_refresh_token"
            }
    }
