#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import json
from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
from enum import Enum
from functools import total_ordering
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Tuple, TypeVar, Union

import pendulum
import pydantic
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy
from airbyte_cdk.sources.streams.core import package_name_from_class
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.utils.schema_helpers import ResourceSchemaLoader
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer

# TikTok Initial release date is September 2016
DEFAULT_START_DATE = "2016-09-01"
DEFAULT_END_DATE = str(datetime.now().date())
NOT_AUDIENCE_METRICS = [
    "reach",
    "cost_per_1000_reached",
    "frequency",
    "secondary_goal_result",
    "cost_per_secondary_goal_result",
    "secondary_goal_result_rate",
    "cash_spend",
    "voucher_spend",
    "video_play_actions",
    "video_watched_2s",
    "video_watched_6s",
    "average_video_play",
    "average_video_play_per_user",
    "video_views_p25",
    "video_views_p50",
    "video_views_p75",
    "video_views_p100",
    "profile_visits",
    "likes",
    "comments",
    "shares",
    "follows",
    "clicks_on_music_disc",
    "real_time_app_install",
    "real_time_app_install_cost",
    "app_install",
]

T = TypeVar("T")


# Hierarchy of classes
# TiktokStream
# ├─AdvertiserIds AdvertiserIds
# └─FullRefreshTiktokStream
#   ├─Advertisers                             (1 advertisers)
#   └─IncrementalTiktokStream
#     ├─AdGroups                              (2 ad_groups)
#     ├─Ads                                   (3 ads)
#     ├─Campaigns                             (4 campaigns)
#     └─BasicReports
#       ├─AdsReports                          (5 ads_reports)
#       ├─AdvertisersReports                  (6 advertisers_reports)
#       ├─CampaignsReports                    (7 campaigns_reports)
#       ├─AdGroupsReports                     (8 ad_groups_reports)
#       └─AudienceReport
#         ├─AdGroupAudienceReports            (9 ad_group_audience_reports)
#         ├─AdsAudienceReports                (10 ads_audience_reports)
#         ├─AdvertisersAudienceReports        (11 advertisers_audience_reports)
#         └─CampaignsAudienceReportsByCountry (12 campaigns_audience_reports_by_country)


@total_ordering
class JsonUpdatedState(pydantic.BaseModel):
    current_stream_state: str
    stream: T

    def __repr__(self):
        """Overrides print view"""
        return str(self.dict())

    def dict(self, **kwargs):
        """Overrides default logic.
        A new updated stage has to be sent if all advertisers are used only
        """
        if not self.stream.is_finished:
            return self.current_stream_state
        max_updated_at = self.stream.max_cursor_date or ""
        return max(max_updated_at, self.current_stream_state)

    def __eq__(self, other):
        if isinstance(other, JsonUpdatedState):
            return self.current_stream_state == other.current_stream_state
        return self.current_stream_state == other

    def __lt__(self, other):
        if isinstance(other, JsonUpdatedState):
            return self.current_stream_state < other.current_stream_state
        return self.current_stream_state < other


class ReportLevel(str, Enum):
    ADVERTISER = "ADVERTISER"
    CAMPAIGN = "CAMPAIGN"
    ADGROUP = "ADGROUP"
    AD = "AD"


class ReportGranularity(str, Enum):
    LIFETIME = "LIFETIME"
    DAY = "DAY"
    HOUR = "HOUR"

    @classmethod
    def default(cls):
        return cls.DAY


class Hourly:
    report_granularity = ReportGranularity.HOUR


class Daily:
    report_granularity = ReportGranularity.DAY


class Lifetime:
    report_granularity = ReportGranularity.LIFETIME


class TiktokException(Exception):
    """default exception for custom Tiktok logic"""


class TiktokStream(HttpStream, ABC):
    # endpoints can have different list names
    response_list_field = "list"

    # max value of page
    page_size = 1000

    def __init__(self, **kwargs):
        super().__init__(authenticator=kwargs.get("authenticator"))

        self._advertiser_id = kwargs.get("advertiser_id")

        # only sandbox has non-empty self._advertiser_id
        self.is_sandbox = bool(self._advertiser_id)

    @property
    def availability_strategy(self) -> Optional["AvailabilityStrategy"]:
        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """All responses have the similar structure:
        {
            "message": "<OK or ERROR>",
            "code": <code>, # 0 if error else error unique code
            "request_id": "<unique_request_id>"
            "data": {
                "page_info": {
                    "total_number": <total_item_count>,
                    "page": <current_page_number>,
                    "page_size": <page_size>,
                    "total_page": <total_page_count>
                },
                "list": [
                    <list_item>
                ]
           }
        }
        """
        data = response.json()
        if data["code"]:
            raise TiktokException(data)
        data = data["data"]
        if self.response_list_field in data:
            data = data[self.response_list_field]
        for record in data:
            yield record

    @property
    def url_base(self) -> str:
        """
        Docs: https://business-api.tiktok.com/marketing_api/docs?id=1701890920013825
        """
        if self.is_sandbox:
            return "https://sandbox-ads.tiktok.com/open_api/v1.2/"
        return "https://business-api.tiktok.com/open_api/v1.2/"

    def next_page_token(self, *args, **kwargs) -> Optional[Mapping[str, Any]]:
        # this data without listing
        return None

    def should_retry(self, response: requests.Response) -> bool:
        """
        Once the rate limit is met, the server returns "code": 40100
        Docs: https://business-api.tiktok.com/marketing_api/docs?id=1701890997610497
        Retry 50002 as well - it's a server error.
        """
        try:
            data = response.json()
        except Exception:
            self.logger.error(f"Incorrect JSON response: {response.text}")
            raise
        if data["code"] in (40100, 50002):
            return True
        return super().should_retry(response)

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        """
        The system uses a second call limit for each developer app. The set limit varies according to the app's call limit level.
        """
        # Basic: 	10/sec
        # Advanced: 	20/sec
        # Premium: 	30/sec
        # All apps are set to basic call limit level by default.
        # Returns maximum possible delay
        return 0.6


class AdvertiserIds(TiktokStream):
    """Loading of all possible advertiser ids"""

    primary_key = "advertiser_id"
    use_cache = True  # it is used in all streams

    def __init__(self, app_id: int, secret: str, access_token: str, **kwargs):
        super().__init__(advertiser_id=0, authenticator=None)

        # for Production env
        self._secret = secret
        self._app_id = app_id
        self._access_token = access_token

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        return {"access_token": self._access_token, "secret": self._secret, "app_id": self._app_id}

    def path(self, *args, **kwargs) -> str:
        return "oauth2/advertiser/get/"


class FullRefreshTiktokStream(TiktokStream, ABC):
    primary_key = "id"
    fields: List[str] = None

    transformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization | TransformConfig.CustomSchemaNormalization)

    @transformer.registerCustomTransform
    def transform_function(original_value: Any, field_schema: Dict[str, Any]) -> Any:
        """Custom traun"""
        if original_value == "-":
            return None
        elif isinstance(original_value, float):
            return Decimal(original_value)
        return original_value

    def __init__(self, start_date: str, end_date: str, **kwargs):
        super().__init__(**kwargs)
        self.kwargs = kwargs
        # convert a start date to TikTok format
        # example:  "2021-08-24" => "2021-08-24 00:00:00"
        self._start_time = pendulum.parse(start_date or DEFAULT_START_DATE).strftime("%Y-%m-%d 00:00:00")
        # convert end date to TikTok format
        # example:  "2021-08-24" => "2021-08-24 00:00:00"
        self._end_time = pendulum.parse(end_date or DEFAULT_END_DATE).strftime("%Y-%m-%d 00:00:00")
        self.max_cursor_date = None
        self._advertiser_ids = []

    @staticmethod
    def convert_array_param(arr: List[Union[str, int]]) -> str:
        return json.dumps(arr)

    def get_advertiser_ids(self) -> Iterable[int]:
        if self.is_sandbox:
            # for sandbox: just return advertiser_id provided in spec
            ids = [self._advertiser_id]
        else:
            # for prod: return list of all available ids from AdvertiserIds stream:
            advertiser_ids = AdvertiserIds(**self.kwargs).read_records(sync_mode=SyncMode.full_refresh)
            ids = [advertiser["advertiser_id"] for advertiser in advertiser_ids]

        self._advertiser_ids = ids
        return ids

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        """Each stream slice is for separate advertiser id"""
        self.get_advertiser_ids()
        while self._advertiser_ids:
            # self._advertiser_ids need to be exhausted so that JsonUpdatedState knows
            # when all stream slices are processed (stream.is_finished)
            advertiser_id = self._advertiser_ids.pop(0)
            yield {"advertiser_id": advertiser_id}

    @property
    def is_finished(self):
        return len(self._advertiser_ids) == 0

    def request_params(
        self,
        stream_state: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        **kwargs,
    ) -> MutableMapping[str, Any]:
        params = {"page_size": self.page_size}
        if self.fields:
            params["fields"] = self.convert_array_param(self.fields)
        if stream_slice:
            params.update(stream_slice)
        return params


class IncrementalTiktokStream(FullRefreshTiktokStream, ABC):
    cursor_field = "modify_time"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """All responses have the following pagination data:
        {
            "data": {
                "page_info": {
                    "total_number": < total_item_count >,
                    "page": < current_page_number >,
                    "page_size": < page_size >,
                    "total_page": < total_page_count >
                },
                ...
           }
        }
        """

        page_info = response.json()["data"]["page_info"]
        if page_info["page"] < page_info["total_page"]:
            return {"page": page_info["page"] + 1}
        return None

    def request_params(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(next_page_token=next_page_token, **kwargs)
        if next_page_token:
            params.update(next_page_token)
        return params

    def select_cursor_field_value(self, data: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None) -> str:
        if not data or not self.cursor_field:
            return None

        cursor_field_path = self.cursor_field if isinstance(self.cursor_field, list) else [self.cursor_field]

        # backward capability to support old state objects
        if "dimensions" in data:
            cursor_field_path = self.deprecated_cursor_field

        result = data
        for key in cursor_field_path:
            result = result.get(key)
        return result

    @staticmethod
    def unnest_field(record: Mapping[str, Any], unnest_from: str, fields: Iterable[str]):
        """
        Unnest cursor_field to the root level of the record.
        """
        if unnest_from in record:
            prop = record.get(unnest_from, {})
            for field in fields:
                if field in prop:
                    record[field] = prop.get(field)

    def parse_response(
        self, response: requests.Response, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, **kwargs
    ) -> Iterable[Mapping]:
        """Additional data filtering"""
        state = self.select_cursor_field_value(stream_state) or self._start_time
        for record in super().parse_response(response=response, stream_state=stream_state, **kwargs):
            # unnest nested cursor_field and primary_key from nested `dimensions` object to root-level for *_reports streams
            self.unnest_field(record, "dimensions", [self.cursor_field, self.primary_key])
            updated = self.select_cursor_field_value(record, stream_slice)
            if updated is None:
                yield record
            elif updated <= state:
                continue
            else:
                if not self.max_cursor_date or self.max_cursor_date < updated:
                    self.max_cursor_date = updated
                yield record

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        # needs to save a last state if all advertisers are used before only
        current_stream_state_value = (self.select_cursor_field_value(current_stream_state)) or ""

        # a object JsonUpdatedState is related with a current stream and should return a new updated state if needed
        if not isinstance(current_stream_state_value, JsonUpdatedState):
            current_stream_state_value = JsonUpdatedState(stream=self, current_stream_state=current_stream_state_value)

        # reports streams have cursor fields which be allocated into a nested object
        cursor_field_path = self.cursor_field if isinstance(self.cursor_field, list) else [self.cursor_field]
        # generate a dict with nested items
        # ["key1", "key1"] => {"key1": {"key2": <value>}}
        tree_dict = current_stream_state_value
        for key in reversed(cursor_field_path):
            tree_dict = {key: tree_dict}
        return tree_dict


class Advertisers(FullRefreshTiktokStream):
    """Docs: https://ads.tiktok.com/marketing_api/docs?id=1708503202263042"""

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(**kwargs)
        params["advertiser_ids"] = self.convert_array_param(self.get_advertiser_ids())
        return params

    def path(self, *args, **kwargs) -> str:
        return "advertiser/info/"

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        """this stream must work with the default slice logic"""
        yield None


class Campaigns(IncrementalTiktokStream):
    """Docs: https://ads.tiktok.com/marketing_api/docs?id=1708582970809346"""

    primary_key = "campaign_id"

    def path(self, *args, **kwargs) -> str:
        return "campaign/get/"


class AdGroups(IncrementalTiktokStream):
    """Docs: https://ads.tiktok.com/marketing_api/docs?id=1708503489590273"""

    primary_key = "adgroup_id"

    def path(self, *args, **kwargs) -> str:
        return "adgroup/get/"


class Ads(IncrementalTiktokStream):
    """Docs: https://ads.tiktok.com/marketing_api/docs?id=1708572923161602"""

    primary_key = "ad_id"

    def path(self, *args, **kwargs) -> str:
        return "ad/get/"


class BasicReports(IncrementalTiktokStream, ABC):
    """Docs: https://ads.tiktok.com/marketing_api/docs?id=1707957200780290"""

    primary_key = "ad_id"
    schema_name = "basic_reports"
    report_granularity = None

    def __init__(self, **kwargs):
        report_granularity = kwargs.pop("report_granularity", None)
        super().__init__(**kwargs)

        # Important:
        # for >= 0.1.13 - granularity is set via inheritance
        # for < 0.1.13 - granularity is set via init param
        if report_granularity:
            self.report_granularity = report_granularity

    @property
    @abstractmethod
    def report_level(self) -> ReportLevel:
        """
        Returns a necessary level value
        """

    @property
    def deprecated_cursor_field(self):
        if self.report_granularity == ReportGranularity.DAY:
            return ["dimensions", "stat_time_day"]
        if self.report_granularity == ReportGranularity.HOUR:
            return ["dimensions", "stat_time_hour"]
        if self.report_granularity == ReportGranularity.LIFETIME:
            return ["dimensions", "stat_time_day"]

    @property
    def cursor_field(self):
        if self.report_granularity == ReportGranularity.DAY:
            return "stat_time_day"
        if self.report_granularity == ReportGranularity.HOUR:
            return "stat_time_hour"
        if self.report_granularity == ReportGranularity.LIFETIME:
            return "stat_time_day"

    @staticmethod
    def _get_time_interval(
        start_date: Union[datetime, str], ending_date: Union[datetime, str], granularity: ReportGranularity
    ) -> Iterable[Tuple[datetime, datetime]]:
        """Due to time range restrictions based on the level of granularity of reports, we have to chunk API calls in order
        to get the desired time range.
        Docs: https://ads.tiktok.com/marketing_api/docs?id=1714590313280513
        :param start_date - Timestamp from which we should start the report
        :param granularity - Level of granularity of the report; one of [HOUR, DAY, LIFETIME]
        :return Iterator for pair of start_date and end_date that can be used as request parameters
        """
        if isinstance(start_date, str):
            start_date = pendulum.parse(start_date)
        end_date = pendulum.parse(ending_date) if ending_date else pendulum.now()

        # TikTok API only allows certain amount of days of data based on the reporting granularity
        if granularity == ReportGranularity.DAY:
            max_interval = 30
        elif granularity == ReportGranularity.HOUR:
            max_interval = 1
        elif granularity == ReportGranularity.LIFETIME:
            max_interval = 364
        else:
            raise ValueError(f"Unsupported reporting granularity: {granularity}, must be one of DAY, HOUR, LIFETIME")

        # for incremental sync with abnormal state produce at least one state message
        # by producing at least one stream slice from today
        if end_date < start_date:
            start_date = end_date

        total_date_diff = end_date - start_date

        iterations = total_date_diff.days // max_interval

        for i in range(iterations + 1):
            chunk_start = start_date + pendulum.duration(days=(i * max_interval))
            chunk_end = min(chunk_start + pendulum.duration(days=max_interval, seconds=-1), end_date)
            yield chunk_start, chunk_end

    def _get_reporting_dimensions(self):
        result = []
        spec_id_dimensions = {
            ReportLevel.ADVERTISER: "advertiser_id",
            ReportLevel.CAMPAIGN: "campaign_id",
            ReportLevel.ADGROUP: "adgroup_id",
            ReportLevel.AD: "ad_id",
        }
        if self.report_level and self.report_level in spec_id_dimensions:
            result.append(spec_id_dimensions[self.report_level])

        spec_time_dimensions = {
            ReportGranularity.DAY: "stat_time_day",
            ReportGranularity.HOUR: "stat_time_hour",
        }
        if self.report_granularity and self.report_granularity in spec_time_dimensions:
            result.append(spec_time_dimensions[self.report_granularity])

        return result

    def _get_metrics(self):
        # common metrics for all reporting levels
        result = [
            "spend",
            "cpc",
            "cpm",
            "impressions",
            "clicks",
            "ctr",
            "reach",
            "cost_per_1000_reached",
            "frequency",
            "video_play_actions",
            "video_watched_2s",
            "video_watched_6s",
            "average_video_play",
            "average_video_play_per_user",
            "video_views_p25",
            "video_views_p50",
            "video_views_p75",
            "video_views_p100",
            "profile_visits",
            "likes",
            "comments",
            "shares",
            "follows",
            "clicks_on_music_disc",
            "real_time_app_install",
            "real_time_app_install_cost",
            "app_install",
        ]

        if self.report_level == ReportLevel.ADVERTISER and self.report_granularity == ReportGranularity.DAY:
            # https://ads.tiktok.com/marketing_api/docs?id=1707957200780290
            result.extend(["cash_spend", "voucher_spend"])

        if self.report_level in (ReportLevel.CAMPAIGN, ReportLevel.ADGROUP, ReportLevel.AD):
            result.extend(["campaign_name"])

        if self.report_level in (ReportLevel.ADGROUP, ReportLevel.AD):
            result.extend(
                [
                    "campaign_id",
                    "adgroup_name",
                    "placement",
                    "tt_app_id",
                    "tt_app_name",
                    "mobile_app_id",
                    "promotion_type",
                    "dpa_target_audience_type",
                ]
            )

            result.extend(
                [
                    "conversion",
                    "cost_per_conversion",
                    "conversion_rate",
                    "real_time_conversion",
                    "real_time_cost_per_conversion",
                    "real_time_conversion_rate",
                    "result",
                    "cost_per_result",
                    "result_rate",
                    "real_time_result",
                    "real_time_cost_per_result",
                    "real_time_result_rate",
                    "secondary_goal_result",
                    "cost_per_secondary_goal_result",
                    "secondary_goal_result_rate",
                ]
            )

        if self.report_level == ReportLevel.AD:
            result.extend(["adgroup_id", "ad_name", "ad_text"])

        return result

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        stream_start = self.select_cursor_field_value(stream_state) or self._start_time
        stream_end = self._end_time

        for slice_adv_id in super().stream_slices(**kwargs):
            for start_date, end_date in self._get_time_interval(stream_start, stream_end, self.report_granularity):
                slice = {
                    "advertiser_id": slice_adv_id["advertiser_id"],
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                }
                self.logger.debug(
                    f'name: {self.name}, advertiser_id: {slice["advertiser_id"]}, slice: {slice["start_date"]} - {slice["end_date"]}'
                )
                yield slice

    def path(self, *args, **kwargs) -> str:
        return "reports/integrated/get/"

    def request_params(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, **kwargs)

        params["advertiser_id"] = stream_slice["advertiser_id"]
        params["service_type"] = "AUCTION"
        params["report_type"] = "BASIC"
        params["data_level"] = f"AUCTION_{self.report_level}"
        params["dimensions"] = json.dumps(self._get_reporting_dimensions())
        params["metrics"] = json.dumps(self._get_metrics())
        if self.report_granularity == ReportGranularity.LIFETIME:
            params["lifetime"] = "true"
        else:
            params["start_date"] = stream_slice["start_date"]
            params["end_date"] = stream_slice["end_date"]

        return params

    def get_json_schema(self) -> Mapping[str, Any]:
        """All reports have same schema"""
        return ResourceSchemaLoader(package_name_from_class(AdvertiserIds)).get_schema(self.schema_name)

    def select_cursor_field_value(self, data: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None) -> str:
        if stream_slice:
            return stream_slice["end_date"]
        return super().select_cursor_field_value(data)


class AdsReports(BasicReports):
    """Custom reports for ads"""

    report_level = ReportLevel.AD


class AdvertisersReports(BasicReports):
    """Custom reports for advertiser"""

    primary_key = "advertiser_id"

    report_level = ReportLevel.ADVERTISER


class CampaignsReports(BasicReports):
    """Custom reports for campaigns"""

    primary_key = "campaign_id"

    report_level = ReportLevel.CAMPAIGN


class AdGroupsReports(BasicReports):
    """Custom reports for adgroups"""

    primary_key = "adgroup_id"

    report_level = ReportLevel.ADGROUP


class AudienceReport(BasicReports):
    """Docs: https://ads.tiktok.com/marketing_api/docs?id=1707957217727489"""

    audience_dimensions: List = ["gender", "age"]
    schema_name = "audience_reports"

    def _get_metrics(self):
        result = super()._get_metrics()
        result = [e for e in result if e not in NOT_AUDIENCE_METRICS]
        return result

    def request_params(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, **kwargs)

        dimensions = self._get_reporting_dimensions()
        dimensions += self.audience_dimensions
        params["dimensions"] = json.dumps(dimensions)
        params["report_type"] = "AUDIENCE"

        return params


class AdGroupAudienceReports(AudienceReport):

    primary_key = "adgroup_id"

    report_level = ReportLevel.ADGROUP


class AdsAudienceReports(AudienceReport):

    report_level = ReportLevel.AD


class AdvertisersAudienceReports(AudienceReport):

    primary_key = "advertiser_id"

    report_level = ReportLevel.ADVERTISER


class CampaignsAudienceReportsByCountry(AudienceReport):
    """Custom reports for campaigns by country"""

    primary_key = "campaign_id"

    report_level = ReportLevel.CAMPAIGN
    audience_dimensions = ["country_code"]
