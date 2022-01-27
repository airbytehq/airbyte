#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from datetime import datetime

import pytest
from airbyte_cdk.models import SyncMode
from source_facebook_marketing.streams.async_job import AsyncJob
from source_facebook_marketing.streams import AdsInsights


@pytest.fixture(name="api")
def api_fixture(mocker):
    api = mocker.Mock()
    api.api.ads_insights_throttle = (0, 0)
    return api


class TestBaseInsightsStream:
    def test_init(self, api):
        stream = AdsInsights(api=api, start_date=datetime(2010, 1, 1), end_date=datetime(2011, 1, 1))

        assert not stream.breakdowns
        assert stream.action_breakdowns == AdsInsights.ALL_ACTION_BREAKDOWNS
        assert stream.name == "ads_insights"
        assert stream.primary_key == ["date_start", "ad_id"]

    def test_init_override(self, api):
        stream = AdsInsights(
            api=api,
            start_date=datetime(2010, 1, 1),
            end_date=datetime(2011, 1, 1),
            name="CustomName",
            breakdowns=["test1", "test2"],
            action_breakdowns=["field1", "field2"],
        )

        assert stream.breakdowns == ["test1", "test2"]
        assert stream.action_breakdowns == ["field1", "field2"]
        assert stream.name == "custom_name"
        assert stream.primary_key == ["date_start", "ad_id", "test1", "test2"]

    def test_read_records(self, mocker, api):
        """ 1. yield all from mock
            2. if read slice 2, 3 state not changed
                if read slice 2, 3, 1 state changed to 3
        """
        job = mocker.Mock(spec=AsyncJob)
        job.get_result.return_value = [mocker.Mock(), mocker.Mock(), mocker.Mock()]
        stream = AdsInsights(
            api=api,
            start_date=datetime(2010, 1, 1),
            end_date=datetime(2011, 1, 1),
        )

        records = list(stream.read_records(
            sync_mode=SyncMode.incremental,
            stream_slice={"insight_job": job},
        ))

        assert len(records) == 3

    # def read_records(
    #     self,
    #     sync_mode: SyncMode,
    #     cursor_field: List[str] = None,
    #     stream_slice: Mapping[str, Any] = None,
    #     stream_state: Mapping[str, Any] = None,
    # ) -> Iterable[Mapping[str, Any]]:
    #     job = stream_slice["insight_job"]
    #     for obj in job.get_result():
    #         yield obj.export_all_data()
    #
    #     self._completed_slices.add(job.key)
    #     if job.key == self._next_cursor_value:
    #         self._advance_cursor()

    def test_state(self):
        pass

    # @property
    # def state(self) -> MutableMapping[str, Any]:
    #     if self._cursor_value:
    #         return {
    #             self.cursor_field: self._cursor_value.isoformat(),
    #             "slices": [d.isoformat() for d in self._completed_slices],
    #         }
    #
    #     if self._completed_slices:
    #         return {
    #             "slices": [d.isoformat() for d in self._completed_slices],
    #         }
    #
    #     return {}
    #
    # @state.setter
    # def state(self, value: MutableMapping[str, Any]):
    #     self._cursor_value = pendulum.parse(value[self.cursor_field]).date() if value.get(self.cursor_field) else None
    #     self._completed_slices = set(pendulum.parse(v).date() for v in value.get("slices", []))
    #     self._next_cursor_value = self._get_start_date()

    def test_stream_slices(self):
        pass

    # def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
    #     manager = InsightAsyncJobManager(api=self._api, jobs=self._generate_async_jobs(params=self.request_params()))
    #     for job in manager.completed_jobs():
    #         yield {"insight_job": job}

    # def test_init(self, api):
    #     stream = AdsInsights(api=api, start_date=datetime(2010, 1, 1), end_date=datetime(2011, 1, 1))
    #
    #     assert not stream.breakdowns
    #     assert not stream.action_breakdowns
    #     assert stream.name == "ads_insights"
    #     assert stream.primary_key == ["date_start", "ad_id"]

    def test_get_json_schema(self, api):
        stream = AdsInsights(api=api, start_date=datetime(2010, 1, 1), end_date=datetime(2011, 1, 1))

        schema = stream.get_json_schema()

        assert "device_platform" not in schema["properties"]
        assert "country" not in schema["properties"]
        assert set(stream.fields) - set(schema["properties"].keys())

    def test_get_json_schema_custom(self, api):
        stream = AdsInsights(
            api=api,
            start_date=datetime(2010, 1, 1),
            end_date=datetime(2011, 1, 1),
            breakdowns=["device_platform", "country"]
        )

        schema = stream.get_json_schema()

        assert "device_platform" in schema["properties"]
        assert "country" in schema["properties"]
        assert set(stream.fields) - set(schema["properties"].keys())

    def test_fields(self, api):
        stream = AdsInsights(
            api=api,
            start_date=datetime(2010, 1, 1),
            end_date=datetime(2011, 1, 1),
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
        )

        assert stream.fields == ["account_id", "account_currency"]
