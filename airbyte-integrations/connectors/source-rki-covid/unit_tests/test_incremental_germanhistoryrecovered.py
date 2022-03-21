#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import requests
from airbyte_cdk.models import SyncMode
from pytest import fixture
from datetime import datetime, timedelta
from source_rki_covid.source import IncrementalRkiCovidStream, GermanHistoryRecovered

@fixture
def patch_incremental_german_history_recovered(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(GermanHistoryRecovered, "primary_key", None)


def test_cursor_field(patch_incremental_german_history_recovered):
    config = {"recovered_in_days": 2}
    stream = GermanHistoryRecovered(config)
    expected_cursor_field = "date"
    assert stream.cursor_field == expected_cursor_field


def test_get_updated_state(patch_incremental_german_history_recovered):
    config = {"recovered_in_days": 2}
    stream = GermanHistoryRecovered(config)
    d = datetime.date(datetime.today()) - timedelta(days=1)
    date = {stream.cursor_field: str(d)}
    inputs = {"current_stream_state": date, "latest_record": date}
    expected_state = {stream.cursor_field: str(d)}
    assert stream.get_updated_state(**inputs) == expected_state


def test_parse_response(patch_incremental_german_history_recovered):
    config = {"recovered_in_days": 2}
    stream = GermanHistoryRecovered(config)
    response = requests.get('https://api.corona-zahlen.org/germany/history/recovered/1')
    expected_response = response.json().get("data")
    assert stream.parse_response(response) == expected_response


def test_parse_with_cases(patch_incremental_german_history_recovered):
    config = {"recovered_in_days": 2}
    stream = GermanHistoryRecovered(config)
    expected_stream_path = "germany/history/recovered/"+str(config.get('recovered_in_days'))
    assert stream.path() == expected_stream_path


def test_parse_without_cases(patch_incremental_german_history_recovered):
    config = {}
    stream = GermanHistoryRecovered(config)
    expected_stream_path = "germany/history/recovered/"
    assert stream.path() == expected_stream_path