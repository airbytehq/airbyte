#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from pathlib import Path
from unittest.mock import Mock

import pytest
from smartsheet.models import Sheet


HERE = Path(__file__).parent.absolute()


@pytest.fixture
def response_mock():
    with open(HERE / "response.json") as json_file:
        return json.loads(json_file.read())


@pytest.fixture
def config():
    return {"spreadsheet_id": "id", "credentials": {"access_token": "token"}, "metadata_fields": ["row_id"]}


@pytest.fixture
def get_sheet_mocker(mocker, response_mock):
    def _mocker(api_wrapper, data=None):
        sheet_obj = Sheet(props=response_mock, base_obj=api_wrapper)
        get_sheet_mock = Mock(return_value=sheet_obj)
        mocker.patch.object(api_wrapper, "_get_sheet", data or get_sheet_mock)
        return get_sheet_mock, sheet_obj

    return _mocker
