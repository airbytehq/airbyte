#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from datetime import date, timedelta
from airbyte_cdk.models import SyncMode
from pytest import fixture
from source_taboola_campaign_summary.source import DailyPerCountry


@fixture
def patch_incremental_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(DailyPerCountry, "path", "v0/example_endpoint")
    mocker.patch.object(DailyPerCountry, "primary_key", "test_primary_key")
    mocker.patch.object(DailyPerCountry, "__abstractmethods__", set())


def test_cursor_field(patch_incremental_base_class):
    stream = DailyPerCountry(account_id="account_id")
    expected_cursor_field = "date"
    assert stream.cursor_field == expected_cursor_field


def test_get_updated_state(patch_incremental_base_class):
    stream = DailyPerCountry(account_id="account_id")
    inputs = {"current_stream_state": None, "latest_record": None}
    expected_state = {"date": date.today().strftime("%Y-%m-%d")}
    assert stream.get_updated_state(**inputs) == expected_state


def test_stream_slices(patch_incremental_base_class):
    stream = DailyPerCountry(account_id="account_id")
    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": [], "stream_state": {}}
    expected_stream_slice = [
        { "date": (date.today() - timedelta(days=7)).strftime("%Y-%m-%d") },
        { "date": (date.today() - timedelta(days=6)).strftime("%Y-%m-%d") },
        { "date": (date.today() - timedelta(days=5)).strftime("%Y-%m-%d") },
        { "date": (date.today() - timedelta(days=4)).strftime("%Y-%m-%d") },
        { "date": (date.today() - timedelta(days=3)).strftime("%Y-%m-%d") },
        { "date": (date.today() - timedelta(days=2)).strftime("%Y-%m-%d") },
        { "date": (date.today() - timedelta(days=1)).strftime("%Y-%m-%d") },
    ]
    assert stream.stream_slices(**inputs) == expected_stream_slice


def test_supports_incremental(patch_incremental_base_class, mocker):
    mocker.patch.object(DailyPerCountry, "cursor_field", "dummy_field")
    stream = DailyPerCountry(account_id="account_id")
    assert stream.supports_incremental


def test_source_defined_cursor(patch_incremental_base_class):
    stream = DailyPerCountry(account_id="account_id")
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(patch_incremental_base_class):
    stream = DailyPerCountry(account_id="account_id")
    # TODO: replace this with your expected checkpoint interval
    expected_checkpoint_interval = None
    assert stream.state_checkpoint_interval == expected_checkpoint_interval
