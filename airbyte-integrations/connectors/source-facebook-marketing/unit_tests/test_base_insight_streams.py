#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import datetime

import pendulum
import pytest
from airbyte_cdk.models import SyncMode
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
        assert stream.action_breakdowns == ["action_type", "action_target_id", "action_destination"]
        assert stream.name == "ads_insights"
        assert stream.primary_key == ["date_start", "account_id", "ad_id"]
        assert stream.action_report_time == "mixed"

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
        assert len(generated_jobs) == (end_date - start_date).days + 1
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
        assert len(generated_jobs) == (end_date - start_date).days + 1
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
        schema = stream.get_json_schema()
        assert schema["properties"].keys() == set(["account_currency", "account_id", stream.cursor_field])

    def test_level_custom(self, api):
        stream = AdsInsights(
            api=api,
            start_date=datetime(2010, 1, 1),
            end_date=datetime(2011, 1, 1),
            fields=["account_id", "account_currency"],
            insights_lookback_window=28,
            level="adset"
        )

        assert stream.level == "adset"
