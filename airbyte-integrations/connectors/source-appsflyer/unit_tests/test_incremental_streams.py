#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pendulum
import pytest
from airbyte_cdk.models import SyncMode
from pytest import fixture, raises
from source_appsflyer.fields import *
from source_appsflyer.source import (
    DailyReport,
    GeoReport,
    InAppEvents,
    IncrementalAppsflyerStream,
    Installs,
    PartnersReport,
    RetargetingDailyReport,
    RetargetingGeoReport,
    RetargetingInAppEvents,
    RetargetingInstalls,
    RetargetingPartnersReport,
    UninstallEvents,
)


@fixture
def patch_incremental_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(IncrementalAppsflyerStream, "path", "v0/example_endpoint")
    mocker.patch.object(IncrementalAppsflyerStream, "primary_key", "test_primary_key")
    mocker.patch.object(IncrementalAppsflyerStream, "__abstractmethods__", set())


@pytest.mark.parametrize(
    ("class_", "expected_cursor_field"),
    [
        (IncrementalAppsflyerStream, []),
        (InAppEvents, "event_time"),
        (RetargetingInAppEvents, "event_time"),
        (UninstallEvents, "event_time"),
        (Installs, "install_time"),
        (RetargetingInstalls, "install_time"),
        (PartnersReport, "date"),
        (DailyReport, "date"),
        (GeoReport, "date"),
        (RetargetingPartnersReport, "date"),
        (RetargetingDailyReport, "date"),
        (RetargetingGeoReport, "date"),
    ],
)
def test_cursor_field(patch_incremental_base_class, mocker, class_, expected_cursor_field):
    mocker.patch.object(class_, "__init__", lambda x: None)
    stream = class_()
    assert stream.cursor_field == expected_cursor_field


@pytest.mark.parametrize(
    ("class_", "cursor_field", "date_only", "additional_fields", "retargeting", "currency"),
    [
        (InAppEvents, "event_time", False, additional_fields.raw_data, None, "preferred"),
        (RetargetingInAppEvents, "event_time", False, additional_fields.raw_data, False, "preferred"),
        (UninstallEvents, "event_time", False, additional_fields.uninstall_events, None, "preferred"),
        (Installs, "install_time", False, additional_fields.raw_data, None, "preferred"),
        (RetargetingInstalls, "install_time", False, additional_fields.raw_data, False, "preferred"),
        (PartnersReport, "date", True, None, None, None),
        (DailyReport, "date", True, None, None, None),
        (GeoReport, "date", True, None, None, None),
        (RetargetingPartnersReport, "date", True, None, True, None),
        (RetargetingDailyReport, "date", True, None, True, None),
        (RetargetingGeoReport, "date", True, None, True, None),
    ],
)
def test_request_params(mocker, class_, cursor_field, date_only, additional_fields, retargeting, currency):
    timezone = "UTC"

    def __init__(self):
        self.api_token = "secret"
        self.timezone = pendulum.timezone("UTC")
        self.start_date = pendulum.yesterday(timezone)
        self.end_date = pendulum.today(timezone)

    mocker.patch.object(class_, "__init__", __init__)
    mocker.patch.object(class_, "cursor_field", cursor_field)
    stream = class_()
    start = pendulum.yesterday(timezone)
    end = pendulum.today(timezone)
    inputs = dict()
    inputs["stream_slice"] = {cursor_field: start, cursor_field + "_end": end}
    inputs["next_page_token"] = None
    inputs["stream_state"] = None
    expected_params = dict()
    expected_params["timezone"] = timezone
    expected_params["maximum_rows"] = 1_000_000
    expected_params["from"] = start.to_datetime_string()
    expected_params["to"] = end.to_datetime_string()
    if date_only:
        expected_params["from"] = start.to_date_string()
        expected_params["to"] = end.to_date_string()
    if additional_fields:
        expected_params["additional_fields"] = (",").join(additional_fields)
    if retargeting:
        expected_params["reattr"] = retargeting
    if currency:
        expected_params["currency"] = currency
    assert stream.request_params(**inputs) == expected_params


@pytest.mark.parametrize(
    ("current_stream_state", "latest_record", "expected_state"),
    [
        (dict(event_time="2021-09-09"), dict(event_time="2021-09-09"), dict(event_time="2021-09-09")),
        ({}, dict(event_time="2021-09-09"), dict(event_time="2021-09-09")),
        ({}, {}, {}),
    ],
)
def test_get_updated_state(patch_incremental_base_class, mocker, current_stream_state, latest_record, expected_state):
    def __init__(self):
        self.timezone = pendulum.timezone("UTC")

    mocker.patch.object(IncrementalAppsflyerStream, "__init__", __init__)
    mocker.patch.object(IncrementalAppsflyerStream, "cursor_field", "event_time")
    stream = IncrementalAppsflyerStream()
    inputs = {"current_stream_state": current_stream_state, "latest_record": latest_record}
    assert stream.get_updated_state(**inputs) == expected_state


def test_get_updated_state_exists_current_stream_and_empty_latest_record(patch_incremental_base_class, mocker):
    with raises(TypeError, match=r"Expected (.*) type '(.*)' but returned type '(.*)'."):

        def __init__(self):
            self.timezone = pendulum.timezone("UTC")

        mocker.patch.object(IncrementalAppsflyerStream, "__init__", __init__)
        mocker.patch.object(IncrementalAppsflyerStream, "cursor_field", "event_time")
        stream = IncrementalAppsflyerStream()
        inputs = {"current_stream_state": dict(event_time="2021-09-09"), "latest_record": {"event_time": None}}
        stream.get_updated_state(**inputs)


def test_stream_slices(patch_incremental_base_class, mocker):
    timezone = "UTC"

    def __init__(self):
        self.api_token = "secret"
        self.timezone = pendulum.timezone("UTC")
        self.start_date = pendulum.yesterday("UTC")
        self.end_date = pendulum.today("UTC")

    mocker.patch.object(IncrementalAppsflyerStream, "__init__", __init__)
    mocker.patch.object(IncrementalAppsflyerStream, "cursor_field", "date")
    stream = IncrementalAppsflyerStream()
    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": [], "stream_state": dict(date=pendulum.yesterday(timezone))}
    expected_stream_slice = [{"date": pendulum.yesterday("UTC"), "date_end": pendulum.today("UTC")}]
    assert stream.stream_slices(**inputs) == expected_stream_slice


def test_supports_incremental(patch_incremental_base_class, mocker):
    mocker.patch.object(IncrementalAppsflyerStream, "__init__", lambda x: None)
    mocker.patch.object(IncrementalAppsflyerStream, "cursor_field", "dummy_field")
    stream = IncrementalAppsflyerStream()
    assert stream.supports_incremental


def test_source_defined_cursor(patch_incremental_base_class, mocker):
    mocker.patch.object(IncrementalAppsflyerStream, "__init__", lambda x: None)
    stream = IncrementalAppsflyerStream()
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(patch_incremental_base_class, mocker):
    mocker.patch.object(IncrementalAppsflyerStream, "__init__", lambda x: None)
    stream = IncrementalAppsflyerStream()
    expected_checkpoint_interval = None
    assert stream.state_checkpoint_interval == expected_checkpoint_interval
