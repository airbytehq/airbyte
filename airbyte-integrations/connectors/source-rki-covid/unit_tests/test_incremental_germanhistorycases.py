#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import requests
from airbyte_cdk.models import SyncMode
from pytest import fixture
from datetime import datetime, timedelta
from source_rki_covid.source import IncrementalRkiCovidStream, GermanyHistoryCases

@fixture
def patch_incremental_german_history_cases(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(GermanyHistoryCases, "primary_key", None)


def test_cursor_field(patch_incremental_german_history_cases):
    config = {"cases_in_days": 2}
    stream = GermanyHistoryCases(config)
    expected_cursor_field = "date"
    assert stream.cursor_field == expected_cursor_field


def test_parse_response(patch_incremental_german_history_cases):
    config = {"cases_in_days": 2}
    stream = GermanyHistoryCases(config)
    response = requests.get('https://api.corona-zahlen.org/germany/history/cases/1')
    expected_response = response.json().get("data")
    assert stream.parse_response(response) == expected_response


def test_parse_with_cases(patch_incremental_german_history_cases):
    config = {"cases_in_days": 2}
    stream = GermanyHistoryCases(config)
    expected_stream_path = "germany/history/cases/"+str(config.get('cases_in_days'))
    assert stream.path() == expected_stream_path


def test_parse_without_cases(patch_incremental_german_history_cases):
    config = {}
    stream = GermanyHistoryCases(config)
    expected_stream_path = "germany/history/cases/"
    assert stream.path() == expected_stream_path