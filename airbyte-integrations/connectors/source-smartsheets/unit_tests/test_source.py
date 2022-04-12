#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import json
from itertools import permutations
from unittest.mock import Mock

import pytest
from source_smartsheets.source import SourceSmartsheets


@pytest.fixture
def config():
    return {"access_token": "token", "spreadsheet_id": "id"}


@pytest.fixture(name="catalog")
def configured_catalog():
    stream_mock = Mock()
    stream_mock.name = "test"  # cannot be used in __init__
    return Mock(streams=[Mock(stream=stream_mock)])


columns = [
    {"id": "1101932201830276", "title": "id", "type": "TEXT_NUMBER"},
    {"id": "5605531829200772", "title": "first_name", "type": "TEXT_NUMBER"},
    {"id": "3353732015515524", "title": "last_name", "type": "TEXT_NUMBER"},
]


cells = [
    {"columnId": "1101932201830276", "value": "11"},
    {"columnId": "5605531829200772", "value": "Leonardo"},
    {"columnId": "3353732015515524", "value": "Dicaprio"},
]


@pytest.mark.parametrize("row", permutations(cells))
def test_different_cell_order_produces_one_result(mocker, row, config, catalog):
    sheet = json.dumps({"name": "test", "totalRowCount": 3, "columns": columns, "rows": [{"cells": row}]})
    mocker.patch("smartsheet.Smartsheet", Mock(return_value=Mock(Sheets=Mock(get_sheet=Mock(return_value=sheet)))))
    source = SourceSmartsheets()
    records = [message.record.data for message in source.read(logger=Mock(), config=config, catalog=catalog, state={})]
    assert list(records) == [{"id": "11", "first_name": "Leonardo", "last_name": "Dicaprio"}]
