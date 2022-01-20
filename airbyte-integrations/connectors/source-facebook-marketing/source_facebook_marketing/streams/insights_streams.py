#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import copy
import logging
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Iterator

import airbyte_cdk.sources.utils.casing as casing
import backoff
import pendulum
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.core import package_name_from_class
from airbyte_cdk.sources.utils.schema_helpers import ResourceSchemaLoader
from cached_property import cached_property
from facebook_business.exceptions import FacebookRequestError
from source_facebook_marketing.streams.async_job import InsightAsyncJob, ParentAsyncJob, AsyncJob
from source_facebook_marketing.streams.async_job_manager import InsightAsyncJobManager

from .common import retry_pattern
from .streams import FBMarketingIncrementalStream

logger = logging.getLogger("airbyte")
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

    # Facebook store metrics maximum of 37 months old. Any time range that
    # older that 37 months from current date would result in 400 Bad request
    # HTTP response.
    # https://developers.facebook.com/docs/marketing-api/reference/ad-account/insights/#overview
    INSIGHTS_RETENTION_PERIOD = pendulum.duration(months=37)
    # Facebook freezes insight data 28 days after it was generated, which means that all data
    # from the past 28 days may have changed since we last emitted it, so we retrieve it again.
    INSIGHTS_LOOKBACK_PERIOD = pendulum.duration(days=28)

    action_breakdowns = ALL_ACTION_BREAKDOWNS
    level = "ad"
    action_attribution_windows = ALL_ACTION_ATTRIBUTION_WINDOWS
    time_increment = 1

    breakdowns = []

    def __init__(
            self,
            name: str = None,
            fields: List[str] = None,
            breakdowns: List[str] = None,
            action_breakdowns: List[str] = None,
            **kwargs,
    ):
        super().__init__(**kwargs)
        self._fields = fields
        self.action_breakdowns = action_breakdowns or self.action_breakdowns
        self.breakdowns = breakdowns or self.breakdowns
        self._new_class_name = name

        # state
        self._cursor_value = None
        self._completed_slices = set()

    @property
    def name(self) -> str:
        """ We override stream name to let the user change it via configuration."""
        name = self._new_class_name or self.__class__.__name__
        return casing.camel_to_snake(name)

    def _get_campaign_ids(self, params) -> List[str]:
        campaign_params = copy.deepcopy(params)
        campaign_params.update(fields=["campaign_id"], level="campaign")
        result = self._api.account.get_insights(params=campaign_params)
        return list(set(row["campaign_id"] for row in result))

    def read_records(
            self,
            sync_mode: SyncMode,
            cursor_field: List[str] = None,
            stream_slice: Mapping[str, Any] = None,
            stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """Waits for current job to finish (slice) and yield its result"""
        job = stream_slice["insight_job"]
        for obj in job.get_result():
            obj.export_all_data()
            yield {"RECORD": "something", "date_start": "2019-08-10T00:00:00Z"}

        if job.key == self._next_cursor_value():
            self._advance_cursor()
        else:
            self._completed_slices.add(job.key)

    @property
    def state(self) -> MutableMapping[str, Any]:
        """State getter, the result can be stored by the source"""
        if self._cursor_value:
            return {
                self.cursor_field: self._cursor_value,
                "slices": self._completed_slices,
            }
        return {}

    @state.setter
    def state(self, value: MutableMapping[str, Any]):
        """State setter"""
        self._cursor_value = pendulum.parse(value[self.cursor_field]) if value.get(self.cursor_field) else None
        self._completed_slices = set(pendulum.parse(v) for v in value.get("slices", []))

    def _next_cursor_value(self):
        """"""
        return self.get_start_date() + pendulum.duration(days=self.time_increment)

    def _advance_cursor(self):
        """Iterate over state, find continuing sequence of slices. Get last value, advance cursor there and remove slices from state"""
        date_range = pendulum.period(self._next_cursor_value(), self._end_date)
        for ts_start in date_range.range("days", self.time_increment):
            if ts_start not in self._completed_slices:
                break
            self._completed_slices.remove(ts_start)
            self._cursor_value = ts_start

    def _generate_async_jobs(self, params: Mapping) -> Iterator[AsyncJob]:
        """ Generator of async jobs

        :param params:
        :return:
        """

        date_range = pendulum.period(self.get_start_date(), self._end_date)
        for ts_start in date_range.range("days", self.time_increment):
            if ts_start in self._completed_slices:
                continue
            total_params = {
                **params,
                "time_range": {
                    "since": ts_start.to_date_string(),
                    "until": ts_start.to_date_string() + pendulum.duration(days=self.time_increment - 1),
                },
            }
            yield InsightAsyncJob(self._api.api, edge_object=self._api.account, params=total_params, key=ts_start)

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        """Slice by date periods and schedule async job for each period, run at most MAX_ASYNC_JOBS jobs at the same time.
        This solution for Async was chosen because:
        1. we should commit state after each successful job
        2. we should run as many job as possible before checking for result
        3. we shouldn't proceed to consumption of the next job before previous succeed

        generate slice only if it is not in state,
        when we finished reading slice (in read_records) we check if current slice is the next one and do advance cursor

        when slice is not next one we just update state with it
        to do so source will check state attribute and call get_state,
        """
        manager = InsightAsyncJobManager(api=self._api, jobs=self._generate_async_jobs(params=self.request_params()))
        for job in manager.completed_jobs():
            yield {"insight_job": job}

    def get_start_date(self) -> pendulum.DateTime:
        if self._cursor_value:
            # FIXME: change cursor logic to not update cursor earlier than 28 days, after that we don't need this line
            start_date = self._cursor_value - self.INSIGHTS_LOOKBACK_PERIOD
        else:
            start_date = self._start_date
        if start_date < pendulum.now() - self.INSIGHTS_RETENTION_PERIOD:
            logger.warning(f"Loading insights older then {self.INSIGHTS_RETENTION_PERIOD} is not possible.")
        return max(self._end_date - self.INSIGHTS_RETENTION_PERIOD, start_date)

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
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
        loader = ResourceSchemaLoader(package_name_from_class(self.__class__))
        schema = loader.get_schema("ads_insights")
        if self._fields:
            schema["properties"] = {k: v for k, v in schema["properties"].items() if k in self._fields}
        if self.breakdowns:
            breakdowns_properties = loader.get_schema("ads_insights_breakdowns")["properties"]
            schema["properties"].update({prop: breakdowns_properties[prop] for prop in self.breakdowns})
        return schema

    @cached_property
    def fields(self) -> List[str]:
        """List of fields that we want to query, for now just all properties from stream's schema"""
        if self._fields:
            return self._fields
        schema = ResourceSchemaLoader(package_name_from_class(self.__class__)).get_schema("ads_insights")
        return list(schema.get("properties", {}).keys())


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
