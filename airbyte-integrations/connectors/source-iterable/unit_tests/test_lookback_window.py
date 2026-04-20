#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import freezegun
import pendulum
import pytest
import responses
from source_iterable.streams import (
    EmailBounce,
    EmailClick,
    IterableExportStream,
    IterableExportStreamAdjustableRange,
    IterableExportStreamRanged,
    Templates,
)

from airbyte_cdk.models import SyncMode


# ---------------------------------------------------------------------------
# Concrete test subclasses — the base classes are abstract (ABC), so we need
# minimal concrete implementations to instantiate and test them directly.
# ---------------------------------------------------------------------------


class _ConcreteExportStream(IterableExportStream):
    data_field = "testStream"


class _ConcreteExportStreamRanged(IterableExportStreamRanged):
    data_field = "testStreamRanged"


class _ConcreteExportStreamAdjustable(IterableExportStreamAdjustableRange):
    data_field = "testStreamAdjustable"


# ---------------------------------------------------------------------------
# _get_effective_end_date() — core lookback logic
# ---------------------------------------------------------------------------


@freezegun.freeze_time("2026-03-24 12:00:00", tz_offset=0)
@pytest.mark.parametrize(
    "lookback_window, end_date, expected",
    [
        pytest.param(5, None, "2026-03-24 11:55:00+00:00", id="default_5min_lookback"),
        pytest.param(0, None, "2026-03-24 12:00:00+00:00", id="zero_lookback"),
        pytest.param(15, None, "2026-03-24 11:45:00+00:00", id="custom_15min_lookback"),
        pytest.param(60, None, "2026-03-24 11:00:00+00:00", id="60min_confirms_minutes_not_seconds"),
        pytest.param(5, "2025-06-15T00:00:00", "2025-06-15T00:00:00", id="explicit_end_date_ignores_lookback"),
        pytest.param(9999, "2025-06-15T00:00:00", "2025-06-15T00:00:00", id="large_lookback_ignored_with_end_date"),
    ],
)
def test_get_effective_end_date(lookback_window, end_date, expected):
    stream = _ConcreteExportStream(
        authenticator=None,
        start_date="2020-01-01",
        end_date=end_date,
        lookback_window=lookback_window,
    )

    assert stream._get_effective_end_date() == pendulum.parse(expected)


def test_default_lookback_window_value():
    """The default lookback_window is 5 when not explicitly provided."""
    stream = _ConcreteExportStream(authenticator=None, start_date="2020-01-01")
    assert stream._lookback_window == 5


# ---------------------------------------------------------------------------
# stream_slices() integration — IterableExportStream base class
# ---------------------------------------------------------------------------


@freezegun.freeze_time("2026-03-24 12:00:00", tz_offset=0)
@pytest.mark.parametrize(
    "lookback_window, end_date, expected_end",
    [
        pytest.param(10, None, "2026-03-24 11:50:00+00:00", id="base_10min_lookback"),
        pytest.param(0, None, "2026-03-24 12:00:00+00:00", id="base_zero_lookback"),
        pytest.param(5, "2025-12-31T23:59:59", "2025-12-31T23:59:59", id="base_explicit_end_date"),
    ],
)
def test_export_stream_slices_end_date(lookback_window, end_date, expected_end):
    stream = _ConcreteExportStream(
        authenticator=None,
        start_date="2026-03-24T00:00:00",
        end_date=end_date,
        lookback_window=lookback_window,
    )

    slices = stream.stream_slices(sync_mode=SyncMode.incremental)

    assert len(slices) == 1
    assert slices[0].end_date == pendulum.parse(expected_end)


# ---------------------------------------------------------------------------
# stream_slices() integration — IterableExportStreamRanged (90-day chunks)
# ---------------------------------------------------------------------------


@freezegun.freeze_time("2026-03-24 12:00:00", tz_offset=0)
@pytest.mark.parametrize(
    "lookback_window, end_date, expected_end",
    [
        pytest.param(10, None, "2026-03-24 11:50:00+00:00", id="ranged_10min_lookback"),
        pytest.param(0, None, "2026-03-24 12:00:00+00:00", id="ranged_zero_lookback"),
        pytest.param(5, "2020-06-01T00:00:00", "2020-06-01T00:00:00", id="ranged_explicit_end_date"),
    ],
)
def test_ranged_stream_slices_end_date(lookback_window, end_date, expected_end):
    stream = _ConcreteExportStreamRanged(
        authenticator=None,
        start_date="2020-01-01",
        end_date=end_date,
        lookback_window=lookback_window,
    )

    slices = list(stream.stream_slices(sync_mode=SyncMode.incremental))

    assert slices[-1].end_date == pendulum.parse(expected_end)


# ---------------------------------------------------------------------------
# stream_slices() integration — IterableExportStreamAdjustableRange
# ---------------------------------------------------------------------------


@freezegun.freeze_time("2026-03-24 12:00:00", tz_offset=0)
@pytest.mark.parametrize(
    "lookback_window, expected_generator_end",
    [
        pytest.param(10, "2026-03-24 11:50:00+00:00", id="adjustable_10min_lookback"),
        pytest.param(0, "2026-03-24 12:00:00+00:00", id="adjustable_zero_lookback"),
    ],
)
def test_adjustable_stream_slices_end_date(lookback_window, expected_generator_end):
    stream = _ConcreteExportStreamAdjustable(
        authenticator=None,
        start_date="2026-03-20T00:00:00",
        lookback_window=lookback_window,
    )

    slices = stream.stream_slices(sync_mode=SyncMode.incremental)
    next(iter(slices))  # consume one slice to initialize generator

    assert stream._adjustable_generator._end_date == pendulum.parse(expected_generator_end)


# ---------------------------------------------------------------------------
# Concrete stream classes — lookback propagates to real streams
# ---------------------------------------------------------------------------


@freezegun.freeze_time("2026-03-24 12:00:00", tz_offset=0)
@pytest.mark.parametrize(
    "stream_cls, lookback_window, expected_end",
    [
        pytest.param(EmailBounce, 5, "2026-03-24 11:55:00+00:00", id="email_bounce_5min"),
        pytest.param(EmailClick, 10, "2026-03-24 11:50:00+00:00", id="email_click_10min"),
        pytest.param(Templates, 5, "2026-03-24 11:55:00+00:00", id="templates_5min"),
    ],
)
def test_concrete_stream_effective_end_date(stream_cls, lookback_window, expected_end):
    stream = stream_cls(
        authenticator=None,
        start_date="2026-03-20T00:00:00",
        lookback_window=lookback_window,
    )

    assert stream._get_effective_end_date() == pendulum.parse(expected_end)


@freezegun.freeze_time("2026-03-24 12:00:00", tz_offset=0)
def test_templates_ranged_slices_end_with_lookback():
    """Templates' ranged slices end at now - lookback."""
    stream = Templates(authenticator=None, start_date="2026-01-01T00:00:00", lookback_window=5)

    slices = list(stream.stream_slices(sync_mode=SyncMode.incremental))

    assert slices[-1].end_date == pendulum.parse("2026-03-24 11:55:00+00:00")


# ---------------------------------------------------------------------------
# Config propagation — lookback_window flows from config to streams
# ---------------------------------------------------------------------------


@responses.activate
@pytest.mark.parametrize(
    "config_lookback, expected_lookback",
    [
        pytest.param(7, 7, id="custom_lookback_propagates"),
        pytest.param(0, 0, id="zero_lookback_propagates"),
    ],
)
def test_export_streams_receive_lookback_from_config(config_lookback, expected_lookback):
    from source_iterable.source import SourceIterable

    responses.get("https://api.iterable.com/api/lists", json={"lists": [{"id": 1}]})
    responses.get("https://api.iterable.com/api/lists/getUsers?listId=1", body="user@example.com")

    config = {
        "api_key": "test-key",
        "start_date": "2020-01-01T00:00:00",
        "lookback_window": config_lookback,
    }

    streams = SourceIterable().streams(config=config)
    export_streams = [s for s in streams if isinstance(s, IterableExportStream)]

    assert len(export_streams) > 0
    for stream in export_streams:
        assert (
            stream._lookback_window == expected_lookback
        ), f"{stream.name} has lookback_window={stream._lookback_window}, expected {expected_lookback}"


@responses.activate
def test_campaigns_metrics_does_not_have_lookback():
    """CampaignsMetrics extends IterableStream (not IterableExportStream), so no _lookback_window."""
    from source_iterable.source import SourceIterable
    from source_iterable.streams import CampaignsMetrics

    responses.get("https://api.iterable.com/api/lists", json={"lists": [{"id": 1}]})
    responses.get("https://api.iterable.com/api/lists/getUsers?listId=1", body="user@example.com")

    config = {
        "api_key": "test-key",
        "start_date": "2020-01-01T00:00:00",
        "lookback_window": 7,
    }

    streams = SourceIterable().streams(config=config)
    campaigns_metrics = [s for s in streams if isinstance(s, CampaignsMetrics)]

    assert len(campaigns_metrics) == 1
    assert not hasattr(campaigns_metrics[0], "_lookback_window")


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


@freezegun.freeze_time("2026-03-24 00:03:00", tz_offset=0)
def test_lookback_can_push_end_before_start():
    """When lookback pushes end_date before start_date, slice is still created."""
    stream = _ConcreteExportStream(
        authenticator=None,
        start_date="2026-03-24T00:00:00",
        lookback_window=5,
    )

    slices = stream.stream_slices(sync_mode=SyncMode.incremental)

    assert len(slices) == 1
    # 00:03 - 5min = 23:58 previous day, which is before 00:00 start
    assert slices[0].end_date < slices[0].start_date


@freezegun.freeze_time("2026-03-24 12:00:00", tz_offset=0)
def test_state_based_start_with_lookback_end():
    """State-based start_date combined with lookback-adjusted end_date."""
    stream = _ConcreteExportStream(authenticator=None, start_date="2020-01-01", lookback_window=5)

    slices = stream.stream_slices(
        sync_mode=SyncMode.incremental,
        stream_state={"createdAt": "2026-03-20T00:00:00"},
    )

    assert len(slices) == 1
    assert slices[0].start_date == pendulum.parse("2026-03-20T00:00:00")
    assert slices[0].end_date == pendulum.parse("2026-03-24 11:55:00+00:00")
