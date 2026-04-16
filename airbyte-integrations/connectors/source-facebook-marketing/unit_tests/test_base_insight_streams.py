#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import date, datetime, timedelta

import pytest
from freezegun import freeze_time
from source_facebook_marketing.spec import InsightConfig, TimeIncrementPeriod, ValidBreakdowns
from source_facebook_marketing.streams import AdsInsights
from source_facebook_marketing.streams.async_job import AsyncJob, InsightAsyncJob
from source_facebook_marketing.utils import DateInterval

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.core import package_name_from_class
from airbyte_cdk.sources.utils.schema_helpers import ResourceSchemaLoader
from airbyte_cdk.utils.datetime_helpers import AirbyteDateTime, ab_datetime_now, ab_datetime_parse


@pytest.fixture(name="api")
def api_fixture(mocker):
    api = mocker.Mock()
    api.api.ads_insights_throttle = (0, 0)
    return api


@pytest.fixture(name="old_start_date")
def old_start_date_fixture() -> AirbyteDateTime:
    return ab_datetime_now() - timedelta(days=(1123))


@pytest.fixture(name="recent_start_date")
def recent_start_date_fixture() -> AirbyteDateTime:
    return ab_datetime_now() - timedelta(days=10)


@pytest.fixture(name="start_date")
def start_date_fixture() -> AirbyteDateTime:
    return ab_datetime_now() - timedelta(days=12 * 30)


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

    @pytest.mark.parametrize(
        "include_incrementality,expected_windows",
        [
            pytest.param(
                False,
                ["1d_click", "7d_click", "28d_click", "1d_view"],
                id="disabled_uses_default_windows",
            ),
            pytest.param(
                True,
                ["1d_click", "7d_click", "28d_click", "1d_view", "incrementality"],
                id="enabled_appends_incrementality",
            ),
        ],
    )
    def test_include_incrementality(self, api, some_config, include_incrementality, expected_windows):
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2010, 1, 1),
            end_date=datetime(2011, 1, 1),
            insights_lookback_window=28,
            include_incrementality=include_incrementality,
        )

        assert stream.action_attribution_windows == expected_windows
        assert stream.request_params()["action_attribution_windows"] == expected_windows

    def test_init_statuses(self, api, some_config):
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2010, 1, 1),
            end_date=datetime(2011, 1, 1),
            insights_lookback_window=28,
            fields=["account_id", "account_currency"],
            filter_statuses=["ACTIVE", "ARCHIVED"],
        )

        assert stream.request_params()["filtering"] == [{"field": "ad.effective_status", "operator": "IN", "value": ["ACTIVE", "ARCHIVED"]}]

    def test_read_records_all(self, mocker, api, some_config):
        """1. yield all from mock
        2. if read slice 2, 3 state not changed
            if read slice 2, 3, 1 state changed to 3
        """
        job = mocker.Mock(spec=InsightAsyncJob)
        rec = mocker.Mock()
        rec.export_all_data.return_value = {}
        job.get_result.return_value = [rec, rec, rec]
        job.interval = DateInterval(date(2010, 1, 1), date(2010, 1, 1))
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
        job.interval = DateInterval(date(2010, 1, 1), date(2010, 1, 1))
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
        job.interval = DateInterval(date(2010, 1, 1), date(2010, 1, 1))
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
                        "slices": [
                            "2010-01-01",
                            "2010-01-02",
                        ],
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
                        "slices": [
                            "2010-01-01",
                            "2010-01-02",
                        ]
                    }
                },
            ),
            # New format - nested with account_id
            (
                {
                    "unknown_account": {
                        AdsInsights.cursor_field: "2010-10-03",
                        "slices": [
                            "2010-01-01",
                            "2010-01-02",
                        ],
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
                        "slices": [
                            "2010-01-01",
                            "2010-01-02",
                        ]
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
            "unknown_account": {"slices": []},
        }

        stream.state = state
        actual_state = stream.state

        result_state = state if not result_state else result_state
        result_state[some_config["account_ids"][0]]["slices"] = result_state[some_config["account_ids"][0]].get("slices", [])
        result_state["time_increment"] = 1

        assert actual_state == result_state

    def test_stream_slices_no_state(self, api, async_manager_mock, start_date, some_config):
        """Stream will use start_date when there is not state"""
        end_date = start_date + timedelta(weeks=2)
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
        assert generated_jobs[1].interval.start == start_date.date() + timedelta(days=1)

    def test_stream_slices_no_state_close_to_now(self, api, async_manager_mock, recent_start_date, some_config):
        """Stream will use start_date when there is not state and start_date within 28d from now"""
        start_date = recent_start_date
        end_date = ab_datetime_now()
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
        assert generated_jobs[1].interval.start == start_date.date() + timedelta(days=1)

    def test_stream_slices_with_state(self, api, async_manager_mock, start_date, some_config):
        """Stream will use cursor_value from state when there is state"""
        end_date = start_date + timedelta(days=10)
        cursor_value = start_date + timedelta(days=5)
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
        assert len(generated_jobs) == (end_date.date() - start_date.date()).days + 1
        assert generated_jobs[0].interval.start == start_date.date()
        assert generated_jobs[1].interval.start == start_date.date() + timedelta(days=1)

    def test_stream_slices_with_state_close_to_now(self, api, async_manager_mock, recent_start_date, some_config):
        """Stream will use start_date when close to now and start_date close to now"""
        start_date = recent_start_date
        end_date = ab_datetime_now()
        cursor_value = end_date - timedelta(days=1)
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
        assert len(generated_jobs) == (end_date.date() - start_date.date()).days + 1
        assert generated_jobs[0].interval.start == start_date.date()
        assert generated_jobs[1].interval.start == start_date.date() + timedelta(days=1)

    @pytest.mark.parametrize("state_format", ["old_format", "new_format"])
    def test_stream_slices_with_state_and_slices(self, api, async_manager_mock, start_date, some_config, state_format):
        """Stream will use cursor_value from state, but will skip saved slices"""
        end_date = start_date + timedelta(days=40)
        cursor_value = start_date + timedelta(days=32)

        if state_format == "old_format":
            state = {
                AdsInsights.cursor_field: cursor_value.date().isoformat(),
                "slices": [
                    (cursor_value + timedelta(days=1)).date().isoformat(),
                    (cursor_value + timedelta(days=3)).date().isoformat(),
                ],
            }
        else:
            state = {
                "unknown_account": {
                    AdsInsights.cursor_field: cursor_value.date().isoformat(),
                    "slices": [
                        (cursor_value + timedelta(days=1)).date().isoformat(),
                        (cursor_value + timedelta(days=3)).date().isoformat(),
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
        assert (
            len(generated_jobs) == (end_date.date() - (cursor_value.date() - stream.insights_lookback_period)).days + 1
        ), "should be 37 slices because we ignore slices which are within insights_lookback_period"
        assert generated_jobs[0].interval.start == cursor_value.date() - stream.insights_lookback_period
        assert generated_jobs[1].interval.start == cursor_value.date() - stream.insights_lookback_period + timedelta(days=1)

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

    @pytest.mark.parametrize(
        "custom_fields, expected_in_schema, expected_not_in_schema",
        [
            pytest.param(
                ["conversion_leads", "cost_per_objective_result"],
                ["conversion_leads", "cost_per_objective_result", "date_start", "date_stop", "account_id", "ad_id"],
                [],
                id="extra_fields_from_custom_schema",
            ),
            pytest.param(
                ["account_id", "impressions", "conversion_leads"],
                ["account_id", "impressions", "conversion_leads", "date_start", "date_stop", "ad_id"],
                [],
                id="mix_of_base_and_extra_fields",
            ),
            pytest.param(
                ["video_thruplay_watched_actions", "objective_result_rate"],
                ["video_thruplay_watched_actions", "objective_result_rate", "date_start", "date_stop", "account_id", "ad_id"],
                [],
                id="ads_action_stats_and_ads_insights_result_fields",
            ),
            pytest.param(
                ["marketing_messages_delivered", "adset_end"],
                ["marketing_messages_delivered", "adset_end", "date_start", "date_stop", "account_id", "ad_id"],
                [],
                id="numeric_and_string_extra_fields",
            ),
        ],
    )
    def test_get_json_schema_custom_with_extra_fields(self, api, some_config, custom_fields, expected_in_schema, expected_not_in_schema):
        """Test that custom insights streams include extra fields from ads_insights_custom_fields.json"""
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2010, 1, 1),
            end_date=datetime(2011, 1, 1),
            fields=custom_fields,
            insights_lookback_window=28,
        )

        schema = stream.get_json_schema()

        for field in expected_in_schema:
            assert field in schema["properties"], f"Expected field '{field}' to be in schema"
        for field in expected_not_in_schema:
            assert field not in schema["properties"], f"Expected field '{field}' to NOT be in schema"

    def test_get_json_schema_builtin_not_changed(self, api, some_config):
        """Test that built-in Ads Insights stream (no custom fields) does not include extra fields"""
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2010, 1, 1),
            end_date=datetime(2011, 1, 1),
            insights_lookback_window=28,
        )

        schema = stream.get_json_schema()

        # These fields should NOT be in the built-in schema (they are only in ads_insights_custom_fields.json)
        extra_fields = ["conversion_leads", "cost_per_objective_result", "video_thruplay_watched_actions"]
        for field in extra_fields:
            assert field not in schema["properties"], f"Extra field '{field}' should NOT be in built-in schema"

        # But standard fields should still be present
        assert "account_id" in schema["properties"]
        assert "impressions" in schema["properties"]
        assert "actions" in schema["properties"]

    def test_fields_custom_with_objective_results(self, api, some_config):
        """Test that objective_results field is included in schema when requested in custom fields"""
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2010, 1, 1),
            end_date=datetime(2011, 1, 1),
            fields=["objective_results", "impressions"],
            insights_lookback_window=28,
        )

        schema = stream.get_json_schema()
        assert "objective_results" in schema["properties"], "objective_results should be in schema when requested"
        assert "impressions" in schema["properties"], "impressions should be in schema when requested"

    @pytest.mark.parametrize(
        "custom_fields, record, expected_record",
        [
            pytest.param(
                ["objective_results", "impressions"],
                {"results": [{"action_type": "purchase", "value": "10"}], "impressions": 100},
                {"objective_results": [{"action_type": "purchase", "value": "10"}], "impressions": 100},
                id="rename_results_to_objective_results",
            ),
            pytest.param(
                ["objective_results", "results", "impressions"],
                {"results": [{"action_type": "purchase", "value": "10"}], "impressions": 100},
                {"results": [{"action_type": "purchase", "value": "10"}], "impressions": 100},
                id="no_rename_when_results_also_requested",
            ),
            pytest.param(
                ["impressions", "clicks"],
                {"results": [{"action_type": "purchase", "value": "10"}], "impressions": 100},
                {"results": [{"action_type": "purchase", "value": "10"}], "impressions": 100},
                id="no_rename_when_objective_results_not_requested",
            ),
            pytest.param(
                None,
                {"results": [{"action_type": "purchase", "value": "10"}], "impressions": 100},
                {"results": [{"action_type": "purchase", "value": "10"}], "impressions": 100},
                id="no_rename_for_builtin_stream",
            ),
            pytest.param(
                ["objective_results", "impressions"],
                {"impressions": 100, "clicks": 50},
                {"impressions": 100, "clicks": 50},
                id="no_rename_when_results_not_in_record",
            ),
            pytest.param(
                ["objective_results", "impressions"],
                {"objective_results": [{"action_type": "purchase", "value": "10"}], "impressions": 100},
                {"objective_results": [{"action_type": "purchase", "value": "10"}], "impressions": 100},
                id="no_rename_when_objective_results_already_in_record",
            ),
            pytest.param(
                ["objective_results", "impressions"],
                {"results": [{"action_type": "purchase", "value": "10"}], "impressions": 100, "spend": 50.5},
                {"objective_results": [{"action_type": "purchase", "value": "10"}], "impressions": 100, "spend": 50.5},
                id="rename_preserves_other_fields",
            ),
            pytest.param(
                ["objective_results", "impressions"],
                {"results": [], "impressions": 100},
                {"objective_results": [], "impressions": 100},
                id="rename_empty_results_array",
            ),
            pytest.param(
                ["objective_results", "impressions"],
                {"results": [{"action_type": "a", "value": "1"}, {"action_type": "b", "value": "2"}], "impressions": 100},
                {"objective_results": [{"action_type": "a", "value": "1"}, {"action_type": "b", "value": "2"}], "impressions": 100},
                id="rename_multiple_results_items",
            ),
            pytest.param(
                ["impressions"],
                {"results": [{"action_type": "purchase", "value": "10"}], "impressions": 100},
                {"results": [{"action_type": "purchase", "value": "10"}], "impressions": 100},
                id="no_rename_when_objective_results_not_in_custom_fields",
            ),
        ],
    )
    def test_objective_results_renamed_from_results(self, api, some_config, custom_fields, record, expected_record):
        """Test that results field is renamed to objective_results when appropriate conditions are met.

        See: https://github.com/airbytehq/oncall/issues/10126
        """
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2010, 1, 1),
            end_date=datetime(2011, 1, 1),
            fields=custom_fields,
            insights_lookback_window=28,
        )

        transformed_record = stream._transform_objective_results(record)
        assert transformed_record == expected_record

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
            ("2018-01-01", "2020-02-29", "2021-02-02", 28),
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
        start_date = ab_datetime_parse(config_start_date)
        end_date = start_date + timedelta(days=10)
        state = (
            {"unknown_account": {AdsInsights.cursor_field: ab_datetime_parse(saved_cursor_date).isoformat()}} if saved_cursor_date else None
        )
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=start_date,
            end_date=end_date,
            insights_lookback_window=lookback_window,
        )
        stream.state = state
        assert str(stream._get_start_date().get("unknown_account")) == expected_start_date

    @pytest.mark.parametrize(
        "breakdowns, record, expected_record",
        (
            (
                [
                    "body_asset",
                ],
                {"body_asset": {"id": "871246182", "text": "Some text"}},
                {"body_asset": {"id": "871246182", "text": "Some text"}, "body_asset_id": "871246182"},
            ),
            (
                [
                    "call_to_action_asset",
                ],
                {"call_to_action_asset": {"id": "871246182", "name": "Some name"}},
                {"call_to_action_asset": {"id": "871246182", "name": "Some name"}, "call_to_action_asset_id": "871246182"},
            ),
            (
                [
                    "description_asset",
                ],
                {"description_asset": {"id": "871246182", "text": "Some text"}},
                {"description_asset": {"id": "871246182", "text": "Some text"}, "description_asset_id": "871246182"},
            ),
            (
                [
                    "image_asset",
                ],
                {"image_asset": {"id": "871246182", "hash": "hash", "url": "url"}},
                {"image_asset": {"id": "871246182", "hash": "hash", "url": "url"}, "image_asset_id": "871246182"},
            ),
            (
                [
                    "link_url_asset",
                ],
                {"link_url_asset": {"id": "871246182", "website_url": "website_url"}},
                {"link_url_asset": {"id": "871246182", "website_url": "website_url"}, "link_url_asset_id": "871246182"},
            ),
            (
                [
                    "title_asset",
                ],
                {"title_asset": {"id": "871246182", "text": "Some text"}},
                {"title_asset": {"id": "871246182", "text": "Some text"}, "title_asset_id": "871246182"},
            ),
            (
                [
                    "video_asset",
                ],
                {
                    "video_asset": {
                        "id": "871246182",
                        "video_id": "video_id",
                        "url": "url",
                        "thumbnail_url": "thumbnail_url",
                        "video_name": "video_name",
                    }
                },
                {
                    "video_asset": {
                        "id": "871246182",
                        "video_id": "video_id",
                        "url": "url",
                        "thumbnail_url": "thumbnail_url",
                        "video_name": "video_name",
                    },
                    "video_asset_id": "871246182",
                },
            ),
            (
                ["body_asset", "country"],
                {"body_asset": {"id": "871246182", "text": "Some text"}, "country": "country", "dma": "dma"},
                {"body_asset": {"id": "871246182", "text": "Some text"}, "country": "country", "dma": "dma", "body_asset_id": "871246182"},
            ),
        ),
    )
    def test_transform_breakdowns(self, api, some_config, breakdowns, record, expected_record):
        start_date = ab_datetime_parse("2024-01-01")
        end_date = start_date + timedelta(days=10)
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=start_date,
            end_date=end_date,
            insights_lookback_window=1,
            breakdowns=breakdowns,
        )
        assert stream._transform_breakdown(record) == expected_record

    @pytest.mark.parametrize(
        "breakdowns, expect_pks",
        (
            (["body_asset"], ["date_start", "account_id", "ad_id", "body_asset_id"]),
            (["call_to_action_asset"], ["date_start", "account_id", "ad_id", "call_to_action_asset_id"]),
            (["description_asset"], ["date_start", "account_id", "ad_id", "description_asset_id"]),
            (["image_asset"], ["date_start", "account_id", "ad_id", "image_asset_id"]),
            (["link_url_asset"], ["date_start", "account_id", "ad_id", "link_url_asset_id"]),
            (["title_asset"], ["date_start", "account_id", "ad_id", "title_asset_id"]),
            (["video_asset"], ["date_start", "account_id", "ad_id", "video_asset_id"]),
            (
                ["video_asset", "skan_conversion_id", "place_page_id"],
                ["date_start", "account_id", "ad_id", "video_asset_id", "skan_conversion_id", "place_page_id"],
            ),
            (None, ["date_start", "account_id", "ad_id"]),
        ),
    )
    def test_primary_keys(self, api, some_config, breakdowns, expect_pks):
        start_date = ab_datetime_parse("2024-01-01")
        end_date = start_date + timedelta(days=10)
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=start_date,
            end_date=end_date,
            insights_lookback_window=1,
            breakdowns=breakdowns,
        )
        assert stream.primary_key == expect_pks

    @pytest.mark.parametrize(
        "level, expect_pks",
        (
            ("ad", ["date_start", "account_id", "ad_id"]),
            ("adset", ["date_start", "account_id", "adset_id"]),
            ("campaign", ["date_start", "account_id", "campaign_id"]),
            ("account", ["date_start", "account_id"]),
        ),
    )
    def test_primary_keys_by_level(self, api, some_config, level, expect_pks):
        start_date = ab_datetime_parse("2024-01-01")
        end_date = start_date + timedelta(days=10)
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=start_date,
            end_date=end_date,
            insights_lookback_window=1,
            level=level,
        )
        assert stream.primary_key == expect_pks

    @pytest.mark.parametrize(
        "level, breakdowns, expect_pks",
        (
            ("ad", ["country"], ["date_start", "account_id", "ad_id", "country"]),
            ("adset", ["country"], ["date_start", "account_id", "adset_id", "country"]),
            ("campaign", ["age", "gender"], ["date_start", "account_id", "campaign_id", "age", "gender"]),
            ("account", ["country"], ["date_start", "account_id", "country"]),
        ),
    )
    def test_primary_keys_by_level_with_breakdowns(self, api, some_config, level, breakdowns, expect_pks):
        start_date = ab_datetime_parse("2024-01-01")
        end_date = start_date + timedelta(days=10)
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=start_date,
            end_date=end_date,
            insights_lookback_window=1,
            level=level,
            breakdowns=breakdowns,
        )
        assert stream.primary_key == expect_pks

    @pytest.mark.parametrize(
        "level, entity_id_field",
        (
            ("ad", "ad_id"),
            ("adset", "adset_id"),
            ("campaign", "campaign_id"),
            ("account", None),
        ),
    )
    def test_custom_schema_includes_level_entity_id(self, api, some_config, level, entity_id_field):
        start_date = ab_datetime_parse("2024-01-01")
        end_date = start_date + timedelta(days=10)
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=start_date,
            end_date=end_date,
            insights_lookback_window=1,
            level=level,
            fields=["impressions", "clicks"],
        )
        schema = stream.get_json_schema()
        if entity_id_field:
            assert entity_id_field in schema["properties"], f"{entity_id_field} should be in schema for level={level}"
        assert "account_id" in schema["properties"], "account_id should always be in schema"
        assert "date_start" in schema["properties"], "date_start should always be in schema"

    @pytest.mark.parametrize(
        "breakdowns, expect_pks",
        (
            (["body_asset"], ["date_start", "account_id", "ad_id", "body_asset_id"]),
            (["call_to_action_asset"], ["date_start", "account_id", "ad_id", "call_to_action_asset_id"]),
            (["description_asset"], ["date_start", "account_id", "ad_id", "description_asset_id"]),
            (["image_asset"], ["date_start", "account_id", "ad_id", "image_asset_id"]),
            (["link_url_asset"], ["date_start", "account_id", "ad_id", "link_url_asset_id"]),
            (["title_asset"], ["date_start", "account_id", "ad_id", "title_asset_id"]),
            (["video_asset"], ["date_start", "account_id", "ad_id", "video_asset_id"]),
            (
                ["video_asset", "skan_conversion_id", "place_page_id"],
                ["date_start", "account_id", "ad_id", "video_asset_id", "skan_conversion_id", "place_page_id"],
            ),
            (
                ["video_asset", "link_url_asset", "skan_conversion_id", "place_page_id", "gender"],
                [
                    "date_start",
                    "account_id",
                    "ad_id",
                    "video_asset_id",
                    "link_url_asset_id",
                    "skan_conversion_id",
                    "place_page_id",
                    "gender",
                ],
            ),
        ),
    )
    def test_object_pk_added_to_schema(self, api, some_config, breakdowns, expect_pks):
        start_date = ab_datetime_parse("2024-01-01")
        end_date = start_date + timedelta(days=10)
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=start_date,
            end_date=end_date,
            insights_lookback_window=1,
            breakdowns=breakdowns,
        )
        schema = stream.get_json_schema()
        assert schema
        assert stream.primary_key == expect_pks
        for pk in expect_pks:
            assert pk in schema["properties"]

    def test_all_breakdowns_have_schemas(self):
        stream = AdsInsights(
            api=None,
            account_ids=["act_123"],
            start_date=datetime.today().replace(hour=0, minute=0, second=0, microsecond=0),
            end_date=datetime.today().replace(hour=0, minute=0, second=0, microsecond=0),
        )
        loader = ResourceSchemaLoader(package_name_from_class(stream.__class__))
        breakdowns_properties = loader.get_schema("ads_insights_breakdowns")["properties"]

        valid_breakdowns = [breakdown.name for breakdown in ValidBreakdowns]

        # Check for missing breakdowns
        missing_breakdowns = [b for b in valid_breakdowns if b not in breakdowns_properties]
        assert (
            not missing_breakdowns
        ), f"Schema file 'ads_insights_breakdowns.json' is missing definitions for breakdowns: {missing_breakdowns}"


class TestCalendarAlignedPeriods:
    """Tests for the calendar-aligned time period feature (time_increment_period)."""

    # --- Static helper tests ---

    def test_next_monday_on_monday(self):
        """_next_monday returns the same date when it is already Monday."""
        assert AdsInsights._next_monday(date(2026, 3, 2)) == date(2026, 3, 2)  # Monday

    def test_next_monday_on_wednesday(self):
        """_next_monday snaps backward to the previous Monday."""
        assert AdsInsights._next_monday(date(2026, 3, 4)) == date(2026, 3, 2)  # Wednesday -> Monday

    def test_next_monday_on_sunday(self):
        """_next_monday snaps backward to the previous Monday (6 days back)."""
        assert AdsInsights._next_monday(date(2026, 3, 8)) == date(2026, 3, 2)  # Sunday -> Monday

    def test_next_month_start_mid_month(self):
        """_next_month_start returns 1st of next month."""
        assert AdsInsights._next_month_start(date(2026, 3, 15)) == date(2026, 4, 1)

    def test_next_month_start_december(self):
        """_next_month_start handles Dec -> Jan year rollover."""
        assert AdsInsights._next_month_start(date(2026, 12, 15)) == date(2027, 1, 1)

    def test_next_month_start_first_of_month(self):
        """_next_month_start on 1st returns 1st of next month."""
        assert AdsInsights._next_month_start(date(2026, 1, 1)) == date(2026, 2, 1)

    def test_month_end_regular(self):
        """_month_end returns last day of a 31-day month."""
        assert AdsInsights._month_end(date(2026, 3, 1)) == date(2026, 3, 31)

    def test_month_end_february_non_leap(self):
        """_month_end returns Feb 28 for non-leap year."""
        assert AdsInsights._month_end(date(2026, 2, 1)) == date(2026, 2, 28)

    def test_month_end_february_leap(self):
        """_month_end returns Feb 29 for leap year."""
        assert AdsInsights._month_end(date(2028, 2, 1)) == date(2028, 2, 29)

    def test_month_end_april(self):
        """_month_end returns Apr 30 for a 30-day month."""
        assert AdsInsights._month_end(date(2026, 4, 15)) == date(2026, 4, 30)

    # --- _compute_interval_end tests ---

    def test_compute_interval_end_daily(self, api, some_config):
        """Daily period: interval end is the same day (1-day window)."""
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 12, 31),
            insights_lookback_window=28,
            time_increment_period=TimeIncrementPeriod.daily,
        )
        assert stream._compute_interval_end(date(2026, 3, 5)) == date(2026, 3, 5)

    def test_compute_interval_end_weekly(self, api, some_config):
        """Weekly period: interval end is 6 days after start (Mon-Sun)."""
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 12, 31),
            insights_lookback_window=28,
            time_increment_period=TimeIncrementPeriod.weekly,
        )
        # Monday Mar 2 -> Sunday Mar 8
        assert stream._compute_interval_end(date(2026, 3, 2)) == date(2026, 3, 8)

    def test_compute_interval_end_monthly(self, api, some_config):
        """Monthly period: interval end is last day of the month."""
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 12, 31),
            insights_lookback_window=28,
            time_increment_period=TimeIncrementPeriod.monthly,
        )
        assert stream._compute_interval_end(date(2026, 3, 1)) == date(2026, 3, 31)
        assert stream._compute_interval_end(date(2026, 2, 1)) == date(2026, 2, 28)

    def test_compute_interval_end_integer_increment(self, api, some_config):
        """Integer time_increment: interval end is start + N - 1 days."""
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 12, 31),
            insights_lookback_window=28,
            time_increment=7,
        )
        assert stream._compute_interval_end(date(2026, 3, 1)) == date(2026, 3, 7)

    # --- _get_api_time_increment tests ---

    def test_get_api_time_increment_monthly(self, api, some_config):
        """Monthly period passes 'monthly' string to Facebook API."""
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 12, 31),
            insights_lookback_window=28,
            time_increment_period=TimeIncrementPeriod.monthly,
        )
        assert stream._get_api_time_increment() == "monthly"

    def test_get_api_time_increment_weekly(self, api, some_config):
        """Weekly period passes integer 7 to Facebook API."""
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 12, 31),
            insights_lookback_window=28,
            time_increment_period=TimeIncrementPeriod.weekly,
        )
        assert stream._get_api_time_increment() == 7

    def test_get_api_time_increment_daily(self, api, some_config):
        """Daily period passes integer 1 to Facebook API."""
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 12, 31),
            insights_lookback_window=28,
            time_increment_period=TimeIncrementPeriod.daily,
        )
        assert stream._get_api_time_increment() == 1

    def test_get_api_time_increment_none(self, api, some_config):
        """No period: returns integer time_increment."""
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 12, 31),
            insights_lookback_window=28,
            time_increment=5,
        )
        assert stream._get_api_time_increment() == 5

    # --- request_params includes correct time_increment ---

    def test_request_params_monthly_period(self, api, some_config):
        """request_params passes 'monthly' string when period is monthly."""
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 12, 31),
            insights_lookback_window=28,
            time_increment_period=TimeIncrementPeriod.monthly,
        )
        params = stream.request_params()
        assert params["time_increment"] == "monthly"

    def test_request_params_weekly_period(self, api, some_config):
        """request_params passes integer 7 when period is weekly."""
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 12, 31),
            insights_lookback_window=28,
            time_increment_period=TimeIncrementPeriod.weekly,
        )
        params = stream.request_params()
        assert params["time_increment"] == 7

    # --- __init__ time_increment assignment ---

    def test_init_daily_sets_time_increment_1(self, api, some_config):
        """Daily period sets time_increment to 1."""
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 12, 31),
            insights_lookback_window=28,
            time_increment_period=TimeIncrementPeriod.daily,
        )
        assert stream.time_increment == 1
        assert stream.time_increment_period == TimeIncrementPeriod.daily

    def test_init_weekly_sets_time_increment_7(self, api, some_config):
        """Weekly period sets nominal time_increment to 7."""
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 12, 31),
            insights_lookback_window=28,
            time_increment_period=TimeIncrementPeriod.weekly,
        )
        assert stream.time_increment == 7
        assert stream.time_increment_period == TimeIncrementPeriod.weekly

    def test_init_monthly_sets_time_increment_30(self, api, some_config):
        """Monthly period sets nominal time_increment to 30."""
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 12, 31),
            insights_lookback_window=28,
            time_increment_period=TimeIncrementPeriod.monthly,
        )
        assert stream.time_increment == 30
        assert stream.time_increment_period == TimeIncrementPeriod.monthly

    def test_init_no_period_keeps_integer(self, api, some_config):
        """No period: uses integer time_increment as-is."""
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 12, 31),
            insights_lookback_window=28,
            time_increment=14,
        )
        assert stream.time_increment == 14
        assert stream.time_increment_period is None

    # --- _date_intervals tests ---

    @freeze_time("2026-04-01")
    def test_date_intervals_daily(self, api, some_config):
        """Daily period yields every day."""
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2026, 3, 1),
            end_date=datetime(2026, 3, 5),
            insights_lookback_window=28,
            time_increment_period=TimeIncrementPeriod.daily,
        )
        intervals = list(stream._date_intervals(some_config["account_ids"][0]))
        expected = [date(2026, 3, 1), date(2026, 3, 2), date(2026, 3, 3), date(2026, 3, 4), date(2026, 3, 5)]
        assert intervals == expected

    @freeze_time("2026-04-01")
    def test_date_intervals_weekly(self, api, some_config):
        """Weekly period yields Monday-aligned weeks."""
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2026, 3, 4),  # Wednesday
            end_date=datetime(2026, 3, 22),
            insights_lookback_window=28,
            time_increment_period=TimeIncrementPeriod.weekly,
        )
        intervals = list(stream._date_intervals(some_config["account_ids"][0]))
        # Snaps back to Monday Mar 2, then weekly: Mar 2, Mar 9, Mar 16
        expected = [date(2026, 3, 2), date(2026, 3, 9), date(2026, 3, 16)]
        assert intervals == expected

    @freeze_time("2026-04-01")
    def test_date_intervals_monthly(self, api, some_config):
        """Monthly period yields 1st-of-month dates."""
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2026, 1, 15),  # mid-January
            end_date=datetime(2026, 3, 31),
            insights_lookback_window=28,
            time_increment_period=TimeIncrementPeriod.monthly,
        )
        intervals = list(stream._date_intervals(some_config["account_ids"][0]))
        # Snaps to Jan 1, then monthly: Jan 1, Feb 1, Mar 1
        expected = [date(2026, 1, 1), date(2026, 2, 1), date(2026, 3, 1)]
        assert intervals == expected

    @freeze_time("2026-04-01")
    def test_date_intervals_monthly_december_rollover(self, api, some_config):
        """Monthly intervals handle December -> January year boundary."""
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2025, 11, 1),
            end_date=datetime(2026, 2, 28),
            insights_lookback_window=28,
            time_increment_period=TimeIncrementPeriod.monthly,
        )
        intervals = list(stream._date_intervals(some_config["account_ids"][0]))
        expected = [date(2025, 11, 1), date(2025, 12, 1), date(2026, 1, 1), date(2026, 2, 1)]
        assert intervals == expected

    # --- State getter/setter with time_increment_period ---

    def test_state_includes_period(self, api, some_config):
        """State getter includes time_increment_period when set."""
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 12, 31),
            insights_lookback_window=28,
            time_increment_period=TimeIncrementPeriod.weekly,
        )
        state = stream.state
        assert state["time_increment"] == 7
        assert state["time_increment_period"] == "weekly"

    def test_state_no_period_omitted(self, api, some_config):
        """State getter omits time_increment_period when not set."""
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 12, 31),
            insights_lookback_window=28,
        )
        state = stream.state
        assert "time_increment_period" not in state

    def test_state_setter_ignores_mismatched_period(self, api, some_config):
        """State setter discards state when time_increment_period has changed."""
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 12, 31),
            insights_lookback_window=28,
            time_increment_period=TimeIncrementPeriod.weekly,
        )
        # Set state with monthly period (different from current weekly)
        stream.state = {
            "unknown_account": {
                "date_start": "2026-06-01",
                "slices": ["2026-06-01"],
            },
            "time_increment": 30,
            "time_increment_period": "monthly",
        }
        # State should be ignored; cursor_values remains None
        assert stream._cursor_values is None

    def test_state_setter_accepts_matching_period(self, api, some_config):
        """State setter accepts state when time_increment_period matches."""
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 12, 31),
            insights_lookback_window=28,
            time_increment_period=TimeIncrementPeriod.weekly,
        )
        stream.state = {
            "unknown_account": {
                "date_start": "2026-06-01",
                "slices": ["2026-06-01"],
            },
            "time_increment": 7,
            "time_increment_period": "weekly",
        }
        assert stream._cursor_values is not None
        assert stream._cursor_values["unknown_account"] == date(2026, 6, 1)

    def test_state_setter_ignores_mismatched_time_increment(self, api, some_config):
        """State setter discards state when time_increment has changed."""
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 12, 31),
            insights_lookback_window=28,
            time_increment=7,
        )
        # Saved state has time_increment=1 (different from current 7)
        stream.state = {
            "unknown_account": {
                "date_start": "2026-06-01",
                "slices": [],
            },
            "time_increment": 1,
        }
        assert stream._cursor_values is None

    # --- InsightConfig validator tests ---

    def test_insight_config_period_only(self):
        """InsightConfig accepts time_increment_period without time_increment."""
        config = InsightConfig(name="test", time_increment_period="weekly")
        assert config.time_increment_period == TimeIncrementPeriod.weekly

    def test_insight_config_time_increment_only(self):
        """InsightConfig accepts time_increment without time_increment_period."""
        config = InsightConfig(name="test", time_increment=7)
        assert config.time_increment == 7
        assert config.time_increment_period is None

    def test_insight_config_mutual_exclusion_raises(self):
        """InsightConfig raises when both time_increment (non-default) and time_increment_period are set."""
        with pytest.raises(ValueError, match="mutually exclusive"):
            InsightConfig(name="test", time_increment=7, time_increment_period="weekly")

    def test_insight_config_period_with_default_increment_allowed(self):
        """InsightConfig allows time_increment_period when time_increment is at default (1)."""
        config = InsightConfig(name="test", time_increment=1, time_increment_period="monthly")
        assert config.time_increment_period == TimeIncrementPeriod.monthly

    def test_insight_config_neither_set(self):
        """InsightConfig works with neither time_increment_period nor explicit time_increment."""
        config = InsightConfig(name="test")
        assert config.time_increment == 1
        assert config.time_increment_period is None

    def test_init_period_overrides_default_time_increment(self, api, some_config):
        """When time_increment=1 (default) and time_increment_period=weekly, period wins."""
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 12, 31),
            insights_lookback_window=28,
            time_increment=1,
            time_increment_period=TimeIncrementPeriod.weekly,
        )
        assert stream.time_increment == 7
        assert stream.time_increment_period == TimeIncrementPeriod.weekly

    def test_init_monthly_period_overrides_default_time_increment(self, api, some_config):
        """When time_increment=1 (default) and time_increment_period=monthly, period wins."""
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 12, 31),
            insights_lookback_window=28,
            time_increment=1,
            time_increment_period=TimeIncrementPeriod.monthly,
        )
        assert stream.time_increment == 30
        assert stream.time_increment_period == TimeIncrementPeriod.monthly

    def test_state_setter_invalidates_when_period_added(self, api, some_config):
        """Old state without time_increment_period is invalidated when config now has a period."""
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 12, 31),
            insights_lookback_window=28,
            time_increment_period=TimeIncrementPeriod.weekly,
        )
        stream.state = {
            "unknown_account": {
                "date_start": "2026-06-01",
                "slices": ["2026-06-01"],
            },
            "time_increment": 7,
        }
        assert stream._cursor_values is None

    def test_state_setter_invalidates_when_period_removed(self, api, some_config):
        """Old state with time_increment_period is invalidated when config no longer has a period."""
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 12, 31),
            insights_lookback_window=28,
            time_increment=30,
        )
        # Old state has time_increment_period="monthly"
        stream.state = {
            "unknown_account": {
                "date_start": "2026-06-01",
                "slices": ["2026-06-01"],
            },
            "time_increment": 30,
            "time_increment_period": "monthly",
        }

        assert stream._cursor_values is None

    def test_state_setter_accepts_matching_none_period(self, api, some_config):
        """State setter accepts state when both old and new have no time_increment_period."""
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 12, 31),
            insights_lookback_window=28,
            time_increment=7,
        )
        stream.state = {
            "unknown_account": {
                "date_start": "2026-06-01",
                "slices": ["2026-06-01"],
            },
            "time_increment": 7,
        }
        # Both have no period -> state accepted
        assert stream._cursor_values is not None
        assert stream._cursor_values["unknown_account"] == date(2026, 6, 1)

    def test_state_includes_monthly_period(self, api, some_config):
        """State getter includes time_increment_period='monthly' and time_increment=30."""
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 12, 31),
            insights_lookback_window=28,
            time_increment_period=TimeIncrementPeriod.monthly,
        )
        state = stream.state
        assert state["time_increment"] == 30
        assert state["time_increment_period"] == "monthly"

    def test_request_params_daily_period(self, api, some_config):
        """request_params passes integer 1 when period is daily."""
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 12, 31),
            insights_lookback_window=28,
            time_increment_period=TimeIncrementPeriod.daily,
        )
        params = stream.request_params()
        assert params["time_increment"] == 1

    def test_request_params_no_period_uses_integer(self, api, some_config):
        """request_params passes integer time_increment when no period is set."""
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 12, 31),
            insights_lookback_window=28,
            time_increment=14,
        )
        params = stream.request_params()
        assert params["time_increment"] == 14

    @freeze_time("2026-04-01")
    def test_date_intervals_weekly_start_on_monday(self, api, some_config):
        """Weekly period with start_date already on Monday does not snap backward."""
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2026, 3, 2),  # Monday
            end_date=datetime(2026, 3, 22),
            insights_lookback_window=28,
            time_increment_period=TimeIncrementPeriod.weekly,
        )
        intervals = list(stream._date_intervals(some_config["account_ids"][0]))
        expected = [date(2026, 3, 2), date(2026, 3, 9), date(2026, 3, 16)]
        assert intervals == expected

    @freeze_time("2026-04-01")
    def test_date_intervals_monthly_start_on_first(self, api, some_config):
        """Monthly period with start_date on 1st works without snapping."""
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 3, 31),
            insights_lookback_window=28,
            time_increment_period=TimeIncrementPeriod.monthly,
        )
        intervals = list(stream._date_intervals(some_config["account_ids"][0]))
        expected = [date(2026, 1, 1), date(2026, 2, 1), date(2026, 3, 1)]
        assert intervals == expected

    @freeze_time("2026-04-01")
    def test_date_intervals_weekly_narrow_range(self, api, some_config):
        """Weekly period with date range smaller than 7 days yields only the snapped Monday."""
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2026, 3, 5),  # Thursday
            end_date=datetime(2026, 3, 6),  # Friday
            insights_lookback_window=28,
            time_increment_period=TimeIncrementPeriod.weekly,
        )
        intervals = list(stream._date_intervals(some_config["account_ids"][0]))
        # Snaps back to Monday Mar 2, which is <= end_date Mar 6, so yields it
        # Next would be Mar 9 > end_date Mar 6, so stops
        expected = [date(2026, 3, 2)]
        assert intervals == expected

    @freeze_time("2026-04-01")
    def test_date_intervals_clamps_start_to_retention_boundary(self, api, some_config):
        """Start date older than 37-month retention period is clamped forward."""
        # Set start_date well before the retention boundary (4+ years ago).
        # validate_start_date computes retention_date = today - 1123 days + 1 day.
        # Frozen today = 2026-04-01 → retention_date = 2026-04-01 - 1123 + 1 = 2023-03-05.
        retention_date = date(2026, 4, 1) - timedelta(days=1123) + timedelta(days=1)
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2022, 1, 1),  # way before retention boundary
            end_date=datetime(2026, 4, 1),
            insights_lookback_window=0,
            time_increment=5,
        )
        intervals = list(stream._date_intervals(some_config["account_ids"][0]))
        # The first interval should start at the retention boundary, not 2022-01-01
        assert intervals[0] == retention_date
