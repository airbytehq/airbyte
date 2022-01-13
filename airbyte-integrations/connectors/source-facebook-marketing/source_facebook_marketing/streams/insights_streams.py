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
from facebook_business.adobjects.campaign import Campaign
from facebook_business.api import FacebookAdsApiBatch, FacebookRequest, FacebookResponse
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
    INSIGHTS_RETENTION_PERIOD_MONTHS = 37

    action_breakdowns = ALL_ACTION_BREAKDOWNS
    level = "ad"
    action_attribution_windows = ALL_ACTION_ATTRIBUTION_WINDOWS
    time_increment = 1

    breakdowns = []

    def __init__(
            self,
            buffer_days,
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

    @property
    def name(self) -> str:
        """
        :return: Stream name. By default this is the implementing class name, but it can be overridden as needed.
        """
        name = self._new_class_name or self.__class__.__name__
        return casing.camel_to_snake(name)

    @backoff_policy
    def execute_in_batch(self, requests: Iterable[FacebookRequest]) -> List[List[MutableMapping[str, Any]]]:
        """Execute list of requests in batches"""
        records = []
        ad_ids = set()

        def success(response: FacebookResponse):
            # logger.info("GOT data, headers=%s, paging=%s", response.headers(), response.json()["paging"])
            # records.append(response.json()["data"])
            for record in response.json()["data"]:
                ad_ids.add(record["ad_id"])
                records.append({"record": 1, "date_start": record["date_start"], "ad_id": record["ad_id"]})

        def failure(response: FacebookResponse):
            logger.info(f"Request failed with response: {response.body()}")

        api_batch: FacebookAdsApiBatch = self._api.api.new_batch()
        for request in requests:
            api_batch.add_request(request, success=success, failure=failure)

        while api_batch:
            logger.info(f"Batch starting: {pendulum.now()}")
            api_batch = api_batch.execute()
            logger.info(f"Batch executed: {pendulum.now()}")
            if api_batch:
                logger.info("Retry failed requests in batch")

        return records

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
        for obj in stream_slice["insight_job"].get_result():
            yield obj.export_all_data()

    def generate_async_jobs(self, start_date, params) -> Iterator[AsyncJob]:
        date_range = pendulum.period(start_date, self._end_date)
        for ts_start in date_range.range("days", 1):
            total_params = {
                **params,
                "time_range": {
                    "since": ts_start.to_date_string(),
                    "until": ts_start.to_date_string(),
                },
            }
            # campaign_ids = self._get_campaign_ids(params)
            campaign_ids = [6095257740251, 6138749312251, 6150779977051, 6150779978051, 6150779979051, 6150779979251, 6150779980251,
                            6150779980451, 6150779980651, 6150779980851, 6150779981451, 6150779982251, 6150779983051, 6150779983451,
                            6150779992451, 6150779995651, 6150779999251, 6150780000251, 6150780001451, 6150780766051, 6150780767051,
                            6150780769251, 6150780773051, 6150780774051, 6150780784851, 6150780785651, 6150780785851, 6150780786051,
                            6150780786251, 6150780787051, 6150780787251, 6150780788051, 6150780788251, 6150780789051, 6150780789251,
                            6150780789451, 6156940675051, 6156940675251, 6156940675451, 6156940675651, 6156940722851, 6156940723051,
                            6156940723251, 6156940723451, 6156940723651, 6156940769051, 6156940769251, 6156940858051, 6156940858251,
                            6156940944051, 6156940945051, 6156941134051, 6156941134251, 6156941135051, 6156941135251, 6156941267051,
                            6156941268051, 6156941306051, 6156941307051, 6156941308051, 6156941366051]
            # logger.info("PARAMS %s", total_params)
            yield ParentAsyncJob([InsightAsyncJob(Campaign(pk), total_params) for pk in campaign_ids])

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        """Slice by date periods and schedule async job for each period, run at most MAX_ASYNC_JOBS jobs at the same time.
        This solution for Async was chosen because:
        1. we should commit state after each successful job
        2. we should run as many job as possible before checking for result
        3. we shouldn't proceed to consumption of the next job before previous succeed
        """
        jobs = self.generate_async_jobs(
            start_date=self.get_start_date(stream_state),
            params=self.request_params(stream_state=stream_state),
        )
        manager = InsightAsyncJobManager(api=self._api, jobs=jobs)
        for job in manager.completed_jobs:
            yield {"insight_job": job}

    def get_start_date(self, stream_state: Mapping[str, Any]) -> pendulum.DateTime:
        state_value = stream_state.get(self.cursor_field) if stream_state else None
        if state_value:
            """
            Notes: Facebook freezes insight data 28 days after it was generated, which means that all data
            from the past 28 days may have changed since we last emitted it, so we retrieve it again.
            """
            start_date = pendulum.parse(state_value) - pendulum.duration(days=28)
        else:
            start_date = self._start_date
        return max(self._end_date.subtract(months=self.INSIGHTS_RETENTION_PERIOD_MONTHS), start_date)

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
