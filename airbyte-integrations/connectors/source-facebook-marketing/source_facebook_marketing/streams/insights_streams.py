#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

import airbyte_cdk.sources.utils.casing as casing
import backoff
import pendulum
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.core import package_name_from_class
from airbyte_cdk.sources.utils.schema_helpers import ResourceSchemaLoader
from cached_property import cached_property
from facebook_business.exceptions import FacebookRequestError

from .async_job_manager import InsightsAsyncJobManager
from .common import retry_pattern
from .streams import FBMarketingIncrementalStream

backoff_policy = retry_pattern(backoff.expo, FacebookRequestError, max_tries=5, factor=5)


class AdsInsights(FBMarketingIncrementalStream):
    """doc: https://developers.facebook.com/docs/marketing-api/insights"""

    cursor_field = "date_start"
    primary_key = None

    ALL_ACTION_ATTRIBUTION_WINDOWS = [
        "1d_click",
        "7d_click",
        "28d_click",
        "1d_view",
        "7d_view",
        "28d_view",
    ]

    ALL_ACTION_BREAKDOWNS = [
        "action_type",
        "action_target_id",
        "action_destination",
    ]

    # Facebook store metrics maximum of 37 monthes old. Any time range that
    # older that 37 monthes from current date would result in 400 Bad request
    # HTTP response.
    # https://developers.facebook.com/docs/marketing-api/reference/ad-account/insights/#overview
    INSIGHTS_RETENTION_PERIOD_MONTHES = 37

    action_breakdowns = ALL_ACTION_BREAKDOWNS
    level = "ad"
    action_attribution_windows = ALL_ACTION_ATTRIBUTION_WINDOWS
    time_increment = 1

    breakdowns = []

    def __init__(
        self,
        buffer_days,
        days_per_job,
        name: str = None,
        fields: List[str] = None,
        breakdowns: List[str] = None,
        action_breakdowns: List[str] = None,
        **kwargs,
    ):

        super().__init__(**kwargs)
        self.lookback_window = pendulum.duration(days=buffer_days)
        self._fields = fields
        self.action_breakdowns = action_breakdowns or self.action_breakdowns
        self.breakdowns = breakdowns or self.breakdowns
        self._new_class_name = name

    @property
    def name(self) -> str:
        """
        :return: Stream name. By default this is the implementing class name, but it can be overridden as needed.
        """
        name = self._new_class_name or self.__class__.__name__
        return casing.camel_to_snake(name)

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """Waits for current job to finish (slice) and yield its result"""
        job = stream_slice["job"]
        # because we query `lookback_window` days before actual cursor we might get records older then cursor

        for obj in job.get_result():
            yield obj.export_all_data()

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        """Slice by date periods and schedule async job for each period, run at most MAX_ASYNC_JOBS jobs at the same time.
        This solution for Async was chosen because:
        1. we should commit state after each successful job
        2. we should run as many job as possible before checking for result
        3. we shouldn't proceed to consumption of the next job before previous succeed
        """

        job_params = self.request_params(stream_state=stream_state)
        job_manager = InsightsAsyncJobManager(
            api=self._api,
            job_params=job_params,
            from_date=self.get_start_date(stream_state),
            to_date=self._end_date,
        )
        job_manager.add_async_jobs()

        while not job_manager.done():
            yield {"job": job_manager.get_next_completed_job()}

    def get_start_date(self, stream_state: Mapping[str, Any]) -> pendulum.Date:
        state_value = stream_state.get(self.cursor_field) if stream_state else None
        if state_value:
            """
            Notes: Facebook freezes insight data 28 days after it was generated, which means that all data
            from the past 28 days may have changed since we last emitted it, so we retrieve it again.
            """
            start_date = pendulum.parse(state_value) - self.lookback_window
        else:
            start_date = self._start_date
        return max(self._end_date.subtract(months=self.INSIGHTS_RETENTION_PERIOD_MONTHES), start_date)

    def request_params(self, stream_state: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        return {
            "level": self.level,
            "action_breakdowns": self.action_breakdowns,
            "breakdowns": self.breakdowns,
            "fields": self.fields,
            "time_increment": self.time_increment,
            "action_attribution_windows": self.action_attribution_windows,
        }

    def _state_filter(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        """Works differently for insights, so remove it"""
        return {}

    def get_json_schema(self) -> Mapping[str, Any]:
        """Add fields from breakdowns to the stream schema
        :return: A dict of the JSON schema representing this stream.
        """
        schema = ResourceSchemaLoader(package_name_from_class(self.__class__)).get_schema("ads_insights")
        if self._fields:
            schema["properties"] = {k: v for k, v in schema["properties"].items() if k in self._fields}
        schema["properties"].update(self._schema_for_breakdowns())
        return schema

    @cached_property
    def fields(self) -> List[str]:
        """List of fields that we want to query, for now just all properties from stream's schema"""
        if self._fields:
            return self._fields
        schema = ResourceSchemaLoader(package_name_from_class(self.__class__)).get_schema("ads_insights")
        return list(schema.get("properties", {}).keys())

    def _schema_for_breakdowns(self) -> Mapping[str, Any]:
        """Breakdown fields and their type"""
        schemas = {
            "age": {"type": ["null", "integer", "string"]},
            "gender": {"type": ["null", "string"]},
            "country": {"type": ["null", "string"]},
            "dma": {"type": ["null", "string"]},
            "region": {"type": ["null", "string"]},
            "impression_device": {"type": ["null", "string"]},
            "placement": {"type": ["null", "string"]},
            "platform_position": {"type": ["null", "string"]},
            "publisher_platform": {"type": ["null", "string"]},
        }
        breakdowns = self.breakdowns[:]
        if "platform_position" in breakdowns:
            breakdowns.append("placement")

        return {breakdown: schemas[breakdown] for breakdown in self.breakdowns}


class AdsInsightsAgeAndGender(AdsInsights):
    breakdowns = ["age", "gender"]


class AdsInsightsCountry(AdsInsights):
    breakdowns = ["country"]


class AdsInsightsRegion(AdsInsights):
    breakdowns = ["region"]


class AdsInsightsDma(AdsInsights):
    breakdowns = ["dma"]


class AdsInsightsPlatformAndDevice(AdsInsights):
    breakdowns = ["publisher_platform", "platform_position", "impression_device"]
    action_breakdowns = ["action_type"]  # FB Async Job fails for unknown reason if we set other breakdowns


class AdsInsightsActionType(AdsInsights):
    breakdowns = []
    action_breakdowns = ["action_type"]
