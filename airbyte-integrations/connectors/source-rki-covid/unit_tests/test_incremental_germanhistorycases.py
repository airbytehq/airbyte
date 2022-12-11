#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from datetime import datetime

import requests
from pytest import fixture
from source_rki_covid.source import GermanyHistoryCases


@fixture
def patch_incremental_german_history_cases(mocker):
    # Mock abstract methods to enable instantiating abstract class.
    mocker.patch.object(GermanyHistoryCases, "primary_key", None)


def test_cursor_field(patch_incremental_german_history_cases):
    config = {"start_date": "2022-04-27"}
    stream = GermanyHistoryCases(config)
    expected_cursor_field = "date"
    assert stream.cursor_field == expected_cursor_field


def test_parse_response(patch_incremental_german_history_cases):
    config = {"start_date": "2022-04-27"}
    stream = GermanyHistoryCases(config)
    response = requests.get("https://api.corona-zahlen.org/germany/history/cases/1")
    if response.json().get("data"):
        expected_response = response.json().get("data")
        assert stream.parse_response(response) == expected_response
    else:
        expected_response = [{}]
        assert stream.parse_response(response) == expected_response


def check_diff(start_date):
    diff = datetime.now() - datetime.strptime(start_date, "%Y-%m-%d")
    if diff.days <= 0:
        return str(1)
    return str(diff.days)


def test_parse_with_cases(patch_incremental_german_history_cases):
    config = {"start_date": "2022-04-27"}
    stream = GermanyHistoryCases(config)
    expected_stream_path = "germany/history/cases/" + check_diff(config.get("start_date"))
    assert stream.path() == expected_stream_path


def test_parse_without_cases(patch_incremental_german_history_cases):
    config = {}
    stream = GermanyHistoryCases(config)
    expected_stream_path = "germany/history/cases/"
    assert stream.path() == expected_stream_path
