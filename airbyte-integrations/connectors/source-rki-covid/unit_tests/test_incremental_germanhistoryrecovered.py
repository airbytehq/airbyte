#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from datetime import datetime, timedelta

import requests
from pytest import fixture
from source_rki_covid.source import GermanHistoryRecovered


@fixture
def patch_incremental_german_history_recovered(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(GermanHistoryRecovered, "primary_key", None)


def test_cursor_field(patch_incremental_german_history_recovered):
    config = {"start_date": "2022-04-27"}
    stream = GermanHistoryRecovered(config)
    expected_cursor_field = "date"
    assert stream.cursor_field == expected_cursor_field


def test_get_updated_state(patch_incremental_german_history_recovered):
    config = {"start_date": "2022-04-27"}
    stream = GermanHistoryRecovered(config)
    d = datetime.date(datetime.today()) - timedelta(days=1)
    date = {stream.cursor_field: str(d)}
    inputs = {"current_stream_state": date, "latest_record": date}
    expected_state = {stream.cursor_field: str(d)}
    assert stream.get_updated_state(**inputs) == expected_state


def test_parse_response(patch_incremental_german_history_recovered):
    config = {"start_date": "2022-04-27"}
    stream = GermanHistoryRecovered(config)
    response = requests.get("https://api.corona-zahlen.org/germany/history/recovered/1")
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


def test_parse_with_cases(patch_incremental_german_history_recovered):
    config = {"start_date": "2022-04-27"}
    stream = GermanHistoryRecovered(config)
    expected_stream_path = "germany/history/recovered/" + check_diff(config.get("start_date"))
    assert stream.path() == expected_stream_path


def test_parse_without_cases(patch_incremental_german_history_recovered):
    config = {}
    stream = GermanHistoryRecovered(config)
    expected_stream_path = "germany/history/recovered/"
    assert stream.path() == expected_stream_path
