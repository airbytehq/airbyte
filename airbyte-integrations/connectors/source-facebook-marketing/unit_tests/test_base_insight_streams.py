#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import datetime

import pendulum
import pytest
from airbyte_cdk.models import SyncMode
from freezegun import freeze_time
from pendulum import duration
from source_facebook_marketing.streams import AdsInsights
from source_facebook_marketing.streams.async_job import AsyncJob, InsightAsyncJob


@pytest.fixture(name="api")
def api_fixture(mocker):
    api = mocker.Mock()
    api.api.ads_insights_throttle = (0, 0)
    return api


@pytest.fixture(name="old_start_date")
def old_start_date_fixture() -> pendulum.DateTime:
    return pendulum.now() - duration(months=37 + 1)


@pytest.fixture(name="recent_start_date")
def recent_start_date_fixture() -> pendulum.DateTime:
    return pendulum.now() - duration(days=10)


@pytest.fixture(name="start_date")
def start_date_fixture() -> pendulum.DateTime:
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
    def test_init(self, api, some_config):
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2010, 1, 1),
            end_date=datetime(2011, 1, 1),
            insights_lookback_window=28,
        )

        assert not stream.breakdowns
        assert stream.action_breakdowns == [
            "action_type",
            "action_target_id",
            "action_destination",
        ]
        assert stream.name == "ads_insights"
        assert stream.primary_key == ["date_start", "account_id", "ad_id"]
        assert stream.action_report_time == "mixed"

    def test_init_override(self, api, some_config):
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
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
        assert stream.primary_key == [
            "date_start",
            "account_id",
            "ad_id",
            "test1",
            "test2",
        ]

    def test_read_records_all(self, mocker, api, some_config):
        """1. yield all from mock
        2. if read slice 2, 3 state not changed
            if read slice 2, 3, 1 state changed to 3
        """
        job = mocker.Mock(spec=InsightAsyncJob)
        rec = mocker.Mock()
        rec.export_all_data.return_value = {}
        job.get_result.return_value = [rec, rec, rec]
        job.interval = pendulum.Period(pendulum.date(2010, 1, 1), pendulum.date(2010, 1, 1))
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2010, 1, 1),
            end_date=datetime(2011, 1, 1),
            insights_lookback_window=28,
        )

        records = list(
            stream.read_records(
                sync_mode=SyncMode.incremental,
                stream_slice={
                    "insight_job": job,
                    "account_id": some_config["account_ids"][0],
                },
            )
        )

        assert len(records) == 3

    def test_read_records_random_order(self, mocker, api, some_config):
        """1. yield all from mock
        2. if read slice 2, 3 state not changed
            if read slice 2, 3, 1 state changed to 3
        """
        rec = mocker.Mock()
        rec.export_all_data.return_value = {}

        job = mocker.Mock(spec=AsyncJob)
        job.get_result.return_value = [rec, rec, rec]
        job.interval = pendulum.Period(pendulum.date(2010, 1, 1), pendulum.date(2010, 1, 1))
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2010, 1, 1),
            end_date=datetime(2011, 1, 1),
            insights_lookback_window=28,
        )

        records = list(
            stream.read_records(
                sync_mode=SyncMode.incremental,
                stream_slice={
                    "insight_job": job,
                    "account_id": some_config["account_ids"][0],
                },
            )
        )

        assert len(records) == 3

    def test_read_records_add_account_id(self, mocker, api, some_config):
        rec_without_account = mocker.Mock()
        rec_without_account.export_all_data.return_value = {}

        rec_with_account = mocker.Mock()
        rec_with_account.export_all_data.return_value = {"account_id": "some_account_id"}

        job = mocker.Mock(spec=AsyncJob)
        job.get_result.return_value = [rec_without_account, rec_with_account]
        job.interval = pendulum.Period(pendulum.date(2010, 1, 1), pendulum.date(2010, 1, 1))
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2010, 1, 1),
            end_date=datetime(2011, 1, 1),
            insights_lookback_window=28,
        )

        records = list(
            stream.read_records(
                sync_mode=SyncMode.incremental,
                stream_slice={
                    "insight_job": job,
                    "account_id": some_config["account_ids"][0],
                },
            )
        )

        assert len(records) == 2
        for record in records:
            assert record.get("account_id")

    @pytest.mark.parametrize(
        "state,result_state",
        [
            # Old format
            (
                {
                    AdsInsights.cursor_field: "2010-10-03",
                    "slices": [
                        "2010-01-01",
                        "2010-01-02",
                    ],
                    "time_increment": 1,
                },
                {
                    "unknown_account": {
                        AdsInsights.cursor_field: "2010-10-03",
                        "slices": {
                            "2010-01-01",
                            "2010-01-02",
                        },
                    },
                    "time_increment": 1,
                },
            ),
            (
                {
                    AdsInsights.cursor_field: "2010-10-03",
                },
                {
                    "unknown_account": {
                        AdsInsights.cursor_field: "2010-10-03",
                    }
                },
            ),
            (
                {
                    "slices": [
                        "2010-01-01",
                        "2010-01-02",
                    ]
                },
                {
                    "unknown_account": {
                        "slices": {
                            "2010-01-01",
                            "2010-01-02",
                        }
                    }
                },
            ),
            # New format - nested with account_id
            (
                {
                    "unknown_account": {
                        AdsInsights.cursor_field: "2010-10-03",
                        "slices": {
                            "2010-01-01",
                            "2010-01-02",
                        },
                    },
                    "time_increment": 1,
                },
                None,
            ),
            (
                {
                    "unknown_account": {
                        AdsInsights.cursor_field: "2010-10-03",
                    }
                },
                None,
            ),
            (
                {
                    "unknown_account": {
                        "slices": {
                            "2010-01-01",
                            "2010-01-02",
                        }
                    }
                },
                None,
            ),
        ],
    )
    def test_state(self, api, state, result_state, some_config):
        """State setter/getter should work with all combinations"""
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2010, 1, 1),
            end_date=datetime(2011, 1, 1),
            insights_lookback_window=28,
        )

        assert stream.state == {
            "time_increment": 1,
            "unknown_account": {"slices": set()},
        }

        stream.state = state
        actual_state = stream.state

        result_state = state if not result_state else result_state
        result_state[some_config["account_ids"][0]]["slices"] = result_state[some_config["account_ids"][0]].get("slices", set())
        result_state["time_increment"] = 1

        assert actual_state == result_state

    def test_stream_slices_no_state(self, api, async_manager_mock, start_date, some_config):
        """Stream will use start_date when there is not state"""
        end_date = start_date + duration(weeks=2)
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=start_date,
            end_date=end_date,
            insights_lookback_window=28,
        )
        async_manager_mock.completed_jobs.return_value = [1, 2, 3]

        slices = list(stream.stream_slices(stream_state=None, sync_mode=SyncMode.incremental))

        assert slices == [
            {"account_id": "unknown_account", "insight_job": 1},
            {"account_id": "unknown_account", "insight_job": 2},
            {"account_id": "unknown_account", "insight_job": 3},
        ]
        async_manager_mock.assert_called_once()
        args, kwargs = async_manager_mock.call_args
        generated_jobs = list(kwargs["jobs"])
        assert len(generated_jobs) == (end_date - start_date).days + 1
        assert generated_jobs[0].interval.start == start_date.date()
        assert generated_jobs[1].interval.start == start_date.date() + duration(days=1)

    def test_stream_slices_no_state_close_to_now(self, api, async_manager_mock, recent_start_date, some_config):
        """Stream will use start_date when there is not state and start_date within 28d from now"""
        start_date = recent_start_date
        end_date = pendulum.now()
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=start_date,
            end_date=end_date,
            insights_lookback_window=28,
        )
        async_manager_mock.completed_jobs.return_value = [1, 2, 3]

        slices = list(stream.stream_slices(stream_state=None, sync_mode=SyncMode.incremental))

        assert slices == [
            {"account_id": "unknown_account", "insight_job": 1},
            {"account_id": "unknown_account", "insight_job": 2},
            {"account_id": "unknown_account", "insight_job": 3},
        ]
        async_manager_mock.assert_called_once()
        args, kwargs = async_manager_mock.call_args
        generated_jobs = list(kwargs["jobs"])
        assert len(generated_jobs) == (end_date - start_date).days + 1
        assert generated_jobs[0].interval.start == start_date.date()
        assert generated_jobs[1].interval.start == start_date.date() + duration(days=1)

    def test_stream_slices_with_state(self, api, async_manager_mock, start_date, some_config):
        """Stream will use cursor_value from state when there is state"""
        end_date = start_date + duration(days=10)
        cursor_value = start_date + duration(days=5)
        state = {AdsInsights.cursor_field: cursor_value.date().isoformat()}
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=start_date,
            end_date=end_date,
            insights_lookback_window=28,
        )
        async_manager_mock.completed_jobs.return_value = [1, 2, 3]

        slices = list(stream.stream_slices(stream_state=state, sync_mode=SyncMode.incremental))

        assert slices == [
            {"account_id": "unknown_account", "insight_job": 1},
            {"account_id": "unknown_account", "insight_job": 2},
            {"account_id": "unknown_account", "insight_job": 3},
        ]
        async_manager_mock.assert_called_once()
        args, kwargs = async_manager_mock.call_args
        generated_jobs = list(kwargs["jobs"])
        # assert that we sync all periods including insight_lookback_period
        assert len(generated_jobs) == (end_date.date() - start_date).days + 1
        assert generated_jobs[0].interval.start == start_date.date()
        assert generated_jobs[1].interval.start == start_date.date() + duration(days=1)

    def test_stream_slices_with_state_close_to_now(self, api, async_manager_mock, recent_start_date, some_config):
        """Stream will use start_date when close to now and start_date close to now"""
        start_date = recent_start_date
        end_date = pendulum.now()
        cursor_value = end_date - duration(days=1)
        state = {AdsInsights.cursor_field: cursor_value.date().isoformat()}
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=start_date,
            end_date=end_date,
            insights_lookback_window=28,
        )
        async_manager_mock.completed_jobs.return_value = [1, 2, 3]

        slices = list(stream.stream_slices(stream_state=state, sync_mode=SyncMode.incremental))

        assert slices == [
            {"account_id": "unknown_account", "insight_job": 1},
            {"account_id": "unknown_account", "insight_job": 2},
            {"account_id": "unknown_account", "insight_job": 3},
        ]
        async_manager_mock.assert_called_once()
        args, kwargs = async_manager_mock.call_args
        generated_jobs = list(kwargs["jobs"])
        assert len(generated_jobs) == (end_date.date() - start_date).days + 1
        assert generated_jobs[0].interval.start == start_date.date()
        assert generated_jobs[1].interval.start == start_date.date() + duration(days=1)

    @pytest.mark.parametrize("state_format", ["old_format", "new_format"])
    def test_stream_slices_with_state_and_slices(self, api, async_manager_mock, start_date, some_config, state_format):
        """Stream will use cursor_value from state, but will skip saved slices"""
        end_date = start_date + duration(days=40)
        cursor_value = start_date + duration(days=32)

        if state_format == "old_format":
            state = {
                AdsInsights.cursor_field: cursor_value.date().isoformat(),
                "slices": [
                    (cursor_value + duration(days=1)).date().isoformat(),
                    (cursor_value + duration(days=3)).date().isoformat(),
                ],
            }
        else:
            state = {
                "unknown_account": {
                    AdsInsights.cursor_field: cursor_value.date().isoformat(),
                    "slices": [
                        (cursor_value + duration(days=1)).date().isoformat(),
                        (cursor_value + duration(days=3)).date().isoformat(),
                    ],
                }
            }
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=start_date,
            end_date=end_date,
            insights_lookback_window=28,
        )
        async_manager_mock.completed_jobs.return_value = [1, 2, 3]

        slices = list(stream.stream_slices(stream_state=state, sync_mode=SyncMode.incremental))

        assert slices == [
            {"account_id": "unknown_account", "insight_job": 1},
            {"account_id": "unknown_account", "insight_job": 2},
            {"account_id": "unknown_account", "insight_job": 3},
        ]
        async_manager_mock.assert_called_once()
        args, kwargs = async_manager_mock.call_args
        generated_jobs = list(kwargs["jobs"])
        assert len(generated_jobs) == (end_date.date() - (cursor_value.date() - stream.insights_lookback_period)).days + 1, "should be 37 slices because we ignore slices which are within insights_lookback_period"
        assert generated_jobs[0].interval.start == cursor_value.date() - stream.insights_lookback_period
        assert generated_jobs[1].interval.start == cursor_value.date() - stream.insights_lookback_period + duration(days=1)

    def test_get_json_schema(self, api, some_config):
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2010, 1, 1),
            end_date=datetime(2011, 1, 1),
            insights_lookback_window=28,
        )

        schema = stream.get_json_schema()

        assert "device_platform" not in schema["properties"]
        assert "country" not in schema["properties"]
        assert not (set(stream.fields()) - set(schema["properties"].keys())), "all fields present in schema"

    def test_get_json_schema_custom(self, api, some_config):
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2010, 1, 1),
            end_date=datetime(2011, 1, 1),
            breakdowns=["device_platform", "country"],
            insights_lookback_window=28,
        )

        schema = stream.get_json_schema()

        assert "device_platform" in schema["properties"]
        assert "country" in schema["properties"]
        assert not (set(stream.fields()) - set(schema["properties"].keys())), "all fields present in schema"

    def test_fields(self, api, some_config):
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2010, 1, 1),
            end_date=datetime(2011, 1, 1),
            insights_lookback_window=28,
        )

        fields = stream.fields()

        assert "account_id" in fields
        assert "account_currency" in fields
        assert "actions" in fields

    def test_fields_custom(self, api, some_config):
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2010, 1, 1),
            end_date=datetime(2011, 1, 1),
            fields=["account_id", "account_currency"],
            insights_lookback_window=28,
        )

        assert stream.fields() == ["account_id", "account_currency"]
        schema = stream.get_json_schema()
        assert schema["properties"].keys() == set(
            [
                "account_currency",
                "account_id",
                stream.cursor_field,
                "date_stop",
                "ad_id",
            ]
        )

    def test_level_custom(self, api, some_config):
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2010, 1, 1),
            end_date=datetime(2011, 1, 1),
            fields=["account_id", "account_currency"],
            insights_lookback_window=28,
            level="adset",
        )

        assert stream.level == "adset"

    def test_breakdowns_fields_present_in_response_data(self, api, some_config):
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2010, 1, 1),
            end_date=datetime(2011, 1, 1),
            breakdowns=["age", "gender"],
            insights_lookback_window=28,
        )

        data = {"age": "0-100", "gender": "male"}

        assert stream._response_data_is_valid(data)

        data = {"id": "0000001", "name": "Pipenpodl Absakopalis"}

        assert not stream._response_data_is_valid(data)

    @pytest.mark.parametrize(
        "config_start_date, saved_cursor_date, expected_start_date,  lookback_window",
        [
            ("2024-01-01", "2024-02-29", "2024-02-19", 10),
            ("2024-01-01", "2024-02-29", "2024-02-01", 28),
            ("2018-01-01", "2020-02-29", "2021-02-01", 28),
        ],
        ids=[
            "with_stream_state in 37 month interval__stream_state_minus_lookback_10_expected",
            "with_stream_state in 37 month interval__stream_state_minus_lookback_28_expected",
            "with_stream_state NOT in 37 month interval__today_minus_37_month_expected",
        ],
    )
    @freeze_time("2024-03-01")
    def test_start_date_with_lookback_window(
        self, api, some_config, config_start_date: str, saved_cursor_date: str, expected_start_date: str, lookback_window: int
    ):
        start_date = pendulum.parse(config_start_date)
        end_date = start_date + duration(days=10)
        state = (
            {"unknown_account": {AdsInsights.cursor_field: pendulum.parse(saved_cursor_date).isoformat()}} if saved_cursor_date else None
        )
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=start_date,
            end_date=end_date,
            insights_lookback_window=lookback_window,
        )
        stream.state = state
        assert stream._get_start_date().get("unknown_account").to_date_string() == expected_start_date
