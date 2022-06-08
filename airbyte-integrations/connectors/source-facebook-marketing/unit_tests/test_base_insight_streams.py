#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from datetime import datetime

import pendulum
import pytest
import source_facebook_marketing.streams.base_insight_streams
from airbyte_cdk.models import SyncMode
from helpers import FakeInsightAsyncJob, FakeInsightAsyncJobManager, read_full_refresh, read_incremental
from pendulum import duration
from source_facebook_marketing.streams import AdsInsights
from source_facebook_marketing.streams.async_job import AsyncJob, InsightAsyncJob


@pytest.fixture(name="api")
def api_fixture(mocker):
    api = mocker.Mock()
    api.api.ads_insights_throttle = (0, 0)
    return api


@pytest.fixture(name="old_start_date")
def old_start_date_fixture():
    return pendulum.now() - duration(months=37 + 1)


@pytest.fixture(name="recent_start_date")
def recent_start_date_fixture():
    return pendulum.now() - duration(days=10)


@pytest.fixture(name="start_date")
def start_date_fixture():
    return pendulum.now() - duration(months=12)


@pytest.fixture(name="async_manager_mock")
def async_manager_mock_fixture(mocker):
    mock = mocker.patch("source_facebook_marketing.streams.base_insight_streams.InsightAsyncJobManager")
    mock.return_value = mock
    return mock


@pytest.fixture(name="async_job_mock")
def async_job_mock_fixture(mocker):
    mock = mocker.patch("source_facebook_marketing.streams.base_insight_streams.InsightAsyncJob")
    mock.side_effect = lambda api, **kwargs: {"api": api, **kwargs}


class TestBaseInsightsStream:
    def test_init(self, api):
        stream = AdsInsights(api=api, start_date=datetime(2010, 1, 1), end_date=datetime(2011, 1, 1), insights_lookback_window=28)

        assert not stream.breakdowns
        assert stream.action_breakdowns == AdsInsights.ALL_ACTION_BREAKDOWNS
        assert stream.name == "ads_insights"
        assert stream.primary_key == ["date_start", "account_id", "ad_id"]

    def test_init_override(self, api):
        stream = AdsInsights(
            api=api,
            start_date=datetime(2010, 1, 1),
            end_date=datetime(2011, 1, 1),
            name="CustomName",
            breakdowns=["test1", "test2"],
            action_breakdowns=["field1", "field2"],
            insights_lookback_window=28,
        )

        assert stream.breakdowns == ["test1", "test2"]
        assert stream.action_breakdowns == ["field1", "field2"]
        assert stream.name == "custom_name"
        assert stream.primary_key == ["date_start", "account_id", "ad_id", "test1", "test2"]

    def test_read_records_all(self, mocker, api):
        """1. yield all from mock
        2. if read slice 2, 3 state not changed
            if read slice 2, 3, 1 state changed to 3
        """
        job = mocker.Mock(spec=InsightAsyncJob)
        job.get_result.return_value = [mocker.Mock(), mocker.Mock(), mocker.Mock()]
        job.interval = pendulum.Period(pendulum.date(2010, 1, 1), pendulum.date(2010, 1, 1))
        stream = AdsInsights(
            api=api,
            start_date=datetime(2010, 1, 1),
            end_date=datetime(2011, 1, 1),
            insights_lookback_window=28,
        )

        records = list(
            stream.read_records(
                sync_mode=SyncMode.incremental,
                stream_slice={"insight_job": job},
            )
        )

        assert len(records) == 3

    def test_read_records_random_order(self, mocker, api):
        """1. yield all from mock
        2. if read slice 2, 3 state not changed
            if read slice 2, 3, 1 state changed to 3
        """
        job = mocker.Mock(spec=AsyncJob)
        job.get_result.return_value = [mocker.Mock(), mocker.Mock(), mocker.Mock()]
        job.interval = pendulum.Period(pendulum.date(2010, 1, 1), pendulum.date(2010, 1, 1))
        stream = AdsInsights(api=api, start_date=datetime(2010, 1, 1), end_date=datetime(2011, 1, 1), insights_lookback_window=28)

        records = list(
            stream.read_records(
                sync_mode=SyncMode.incremental,
                stream_slice={"insight_job": job},
            )
        )

        assert len(records) == 3

    @pytest.mark.parametrize(
        "state",
        [
            {
                AdsInsights.cursor_field: "2010-10-03",
                "slices": [
                    "2010-01-01",
                    "2010-01-02",
                ],
                "time_increment": 1,
            },
            {
                AdsInsights.cursor_field: "2010-10-03",
            },
            {
                "slices": [
                    "2010-01-01",
                    "2010-01-02",
                ]
            },
        ],
    )
    def test_state(self, api, state):
        """State setter/getter should work with all combinations"""
        stream = AdsInsights(api=api, start_date=datetime(2010, 1, 1), end_date=datetime(2011, 1, 1), insights_lookback_window=28)

        assert stream.state == {}

        stream.state = state
        actual_state = stream.state
        actual_state["slices"] = sorted(actual_state.get("slices", []))
        state["slices"] = sorted(state.get("slices", []))
        state["time_increment"] = 1

        assert actual_state == state

    def test_stream_slices_no_state(self, api, async_manager_mock, start_date):
        """Stream will use start_date when there is not state"""
        end_date = start_date + duration(weeks=2)
        stream = AdsInsights(api=api, start_date=start_date, end_date=end_date, insights_lookback_window=28)
        async_manager_mock.completed_jobs.return_value = [1, 2, 3]

        slices = list(stream.stream_slices(stream_state=None, sync_mode=SyncMode.incremental))

        assert slices == [{"insight_job": 1}, {"insight_job": 2}, {"insight_job": 3}]
        async_manager_mock.assert_called_once()
        args, kwargs = async_manager_mock.call_args
        generated_jobs = list(kwargs["jobs"])
        assert len(generated_jobs) == (end_date - start_date).days + 1
        assert generated_jobs[0].interval.start == start_date.date()
        assert generated_jobs[1].interval.start == start_date.date() + duration(days=1)

    def test_stream_slices_no_state_close_to_now(self, api, async_manager_mock, recent_start_date):
        """Stream will use start_date when there is not state and start_date within 28d from now"""
        start_date = recent_start_date
        end_date = pendulum.now()
        stream = AdsInsights(api=api, start_date=start_date, end_date=end_date, insights_lookback_window=28)
        async_manager_mock.completed_jobs.return_value = [1, 2, 3]

        slices = list(stream.stream_slices(stream_state=None, sync_mode=SyncMode.incremental))

        assert slices == [{"insight_job": 1}, {"insight_job": 2}, {"insight_job": 3}]
        async_manager_mock.assert_called_once()
        args, kwargs = async_manager_mock.call_args
        generated_jobs = list(kwargs["jobs"])
        assert len(generated_jobs) == (end_date - start_date).days
        assert generated_jobs[0].interval.start == start_date.date()
        assert generated_jobs[1].interval.start == start_date.date() + duration(days=1)

    def test_stream_slices_with_state(self, api, async_manager_mock, start_date):
        """Stream will use cursor_value from state when there is state"""
        end_date = start_date + duration(days=10)
        cursor_value = start_date + duration(days=5)
        state = {AdsInsights.cursor_field: cursor_value.date().isoformat()}
        stream = AdsInsights(api=api, start_date=start_date, end_date=end_date, insights_lookback_window=28)
        async_manager_mock.completed_jobs.return_value = [1, 2, 3]

        slices = list(stream.stream_slices(stream_state=state, sync_mode=SyncMode.incremental))

        assert slices == [{"insight_job": 1}, {"insight_job": 2}, {"insight_job": 3}]
        async_manager_mock.assert_called_once()
        args, kwargs = async_manager_mock.call_args
        generated_jobs = list(kwargs["jobs"])
        assert len(generated_jobs) == (end_date - cursor_value).days
        assert generated_jobs[0].interval.start == cursor_value.date() + duration(days=1)
        assert generated_jobs[1].interval.start == cursor_value.date() + duration(days=2)

    def test_stream_slices_with_state_close_to_now(self, api, async_manager_mock, recent_start_date):
        """Stream will use start_date when close to now and start_date close to now"""
        start_date = recent_start_date
        end_date = pendulum.now()
        cursor_value = end_date - duration(days=1)
        state = {AdsInsights.cursor_field: cursor_value.date().isoformat()}
        stream = AdsInsights(api=api, start_date=start_date, end_date=end_date, insights_lookback_window=28)
        async_manager_mock.completed_jobs.return_value = [1, 2, 3]

        slices = list(stream.stream_slices(stream_state=state, sync_mode=SyncMode.incremental))

        assert slices == [{"insight_job": 1}, {"insight_job": 2}, {"insight_job": 3}]
        async_manager_mock.assert_called_once()
        args, kwargs = async_manager_mock.call_args
        generated_jobs = list(kwargs["jobs"])
        assert len(generated_jobs) == (end_date - start_date).days
        assert generated_jobs[0].interval.start == start_date.date()
        assert generated_jobs[1].interval.start == start_date.date() + duration(days=1)

    def test_stream_slices_with_state_and_slices(self, api, async_manager_mock, start_date):
        """Stream will use cursor_value from state, but will skip saved slices"""
        end_date = start_date + duration(days=10)
        cursor_value = start_date + duration(days=5)
        state = {
            AdsInsights.cursor_field: cursor_value.date().isoformat(),
            "slices": [(cursor_value + duration(days=1)).date().isoformat(), (cursor_value + duration(days=3)).date().isoformat()],
        }
        stream = AdsInsights(api=api, start_date=start_date, end_date=end_date, insights_lookback_window=28)
        async_manager_mock.completed_jobs.return_value = [1, 2, 3]

        slices = list(stream.stream_slices(stream_state=state, sync_mode=SyncMode.incremental))

        assert slices == [{"insight_job": 1}, {"insight_job": 2}, {"insight_job": 3}]
        async_manager_mock.assert_called_once()
        args, kwargs = async_manager_mock.call_args
        generated_jobs = list(kwargs["jobs"])
        assert len(generated_jobs) == (end_date - cursor_value).days - 2, "should be 2 slices short because of state"
        assert generated_jobs[0].interval.start == cursor_value.date() + duration(days=2)
        assert generated_jobs[1].interval.start == cursor_value.date() + duration(days=4)

    def test_get_json_schema(self, api):
        stream = AdsInsights(api=api, start_date=datetime(2010, 1, 1), end_date=datetime(2011, 1, 1), insights_lookback_window=28)

        schema = stream.get_json_schema()

        assert "device_platform" not in schema["properties"]
        assert "country" not in schema["properties"]
        assert not (set(stream.fields) - set(schema["properties"].keys())), "all fields present in schema"

    def test_get_json_schema_custom(self, api):
        stream = AdsInsights(
            api=api,
            start_date=datetime(2010, 1, 1),
            end_date=datetime(2011, 1, 1),
            breakdowns=["device_platform", "country"],
            insights_lookback_window=28,
        )

        schema = stream.get_json_schema()

        assert "device_platform" in schema["properties"]
        assert "country" in schema["properties"]
        assert not (set(stream.fields) - set(schema["properties"].keys())), "all fields present in schema"

    def test_fields(self, api):
        stream = AdsInsights(
            api=api,
            start_date=datetime(2010, 1, 1),
            end_date=datetime(2011, 1, 1),
            insights_lookback_window=28,
        )

        fields = stream.fields

        assert "account_id" in fields
        assert "account_currency" in fields
        assert "actions" in fields

    def test_fields_custom(self, api):
        stream = AdsInsights(
            api=api,
            start_date=datetime(2010, 1, 1),
            end_date=datetime(2011, 1, 1),
            fields=["account_id", "account_currency"],
            insights_lookback_window=28,
        )

        assert stream.fields == ["account_id", "account_currency"]

    def test_completed_slices_in_lookback_period(self, api, monkeypatch, set_today):
        start_date = pendulum.parse("2020-03-01")
        end_date = pendulum.parse("2020-05-01")
        set_today("2020-04-01")

        monkeypatch.setattr(source_facebook_marketing.streams.base_insight_streams, "InsightAsyncJob", FakeInsightAsyncJob)
        monkeypatch.setattr(source_facebook_marketing.streams.base_insight_streams, "InsightAsyncJobManager", FakeInsightAsyncJobManager)

        state = {
            AdsInsights.cursor_field: "2020-03-19",
            "slices": [
                "2020-03-21",
                "2020-03-22",
                "2020-03-23",
            ],
            "time_increment": 1,
        }

        stream = AdsInsights(api=api, start_date=start_date, end_date=end_date, insights_lookback_window=10)
        stream.state = state
        assert stream._completed_slices == {pendulum.Date(2020, 3, 21), pendulum.Date(2020, 3, 22), pendulum.Date(2020, 3, 23)}

        slices = stream.stream_slices(stream_state=state, sync_mode=SyncMode.incremental)
        slices = [x["insight_job"].interval.start for x in slices]

        assert pendulum.parse("2020-03-21").date() not in slices
        assert pendulum.parse("2020-03-22").date() in slices
        assert pendulum.parse("2020-03-23").date() in slices
        assert stream._completed_slices == {pendulum.Date(2020, 3, 21)}

    def test_incremental_lookback_period_updated(self, api, monkeypatch, set_today):
        start_date = pendulum.parse("2020-03-01")
        end_date = pendulum.parse("2020-05-01")
        yesterday, _ = set_today("2020-04-01")

        monkeypatch.setattr(source_facebook_marketing.streams.base_insight_streams, "InsightAsyncJob", FakeInsightAsyncJob)
        monkeypatch.setattr(source_facebook_marketing.streams.base_insight_streams, "InsightAsyncJobManager", FakeInsightAsyncJobManager)

        stream = AdsInsights(api=api, start_date=start_date, end_date=end_date, insights_lookback_window=20)

        records = read_full_refresh(stream)
        assert len(records) == (yesterday - start_date).days + 1
        assert records[0]["date_start"] == str(start_date.date())
        assert records[-1]["date_start"] == str(yesterday.date())

        state = {AdsInsights.cursor_field: "2020-03-20", "time_increment": 1}
        records = read_incremental(stream, state)
        assert len(records) == (yesterday - pendulum.parse("2020-03-20")).days
        assert records[0]["date_start"] == "2020-03-21"
        assert records[-1]["date_start"] == str(yesterday.date())
        assert state == {"date_start": str(yesterday.date()), "slices": [], "time_increment": 1}

        yesterday, _ = set_today("2020-04-02")
        records = read_incremental(stream, state)
        assert records == [{"date_start": str(yesterday.date()), "updated_time": str(yesterday.date())}]
        assert state == {"date_start": str(yesterday.date()), "slices": [], "time_increment": 1}

        yesterday, _ = set_today("2020-04-03")
        FakeInsightAsyncJob.update_insight("2020-03-26", "2020-04-01")
        FakeInsightAsyncJob.update_insight("2020-03-27", "2020-04-02")
        FakeInsightAsyncJob.update_insight("2020-03-28", "2020-04-03")

        records = read_incremental(stream, state)
        assert records == [
            {"date_start": "2020-03-27", "updated_time": "2020-04-02"},
            {"date_start": "2020-04-02", "updated_time": "2020-04-02"},
        ]
        assert state == {"date_start": str(yesterday.date()), "slices": [], "time_increment": 1}
