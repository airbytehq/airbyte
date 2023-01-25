#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from datetime import datetime

from pytest import fixture
from source_rki_covid.source import StatesHistoryCases


@fixture
def patch_states_history_cases(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(StatesHistoryCases, "primary_key", None)


def check_diff(start_date):
    diff = datetime.now() - datetime.strptime(start_date, "%Y-%m-%d")
    if diff.days <= 0:
        return str(1)
    return str(diff.days)


def test_parse_with_cases(patch_states_history_cases):
    config = {"start_date": "2022-04-27"}
    stream = StatesHistoryCases(config)
    expected_stream_path = "states/history/cases/" + check_diff(config.get("start_date"))
    assert stream.path() == expected_stream_path
