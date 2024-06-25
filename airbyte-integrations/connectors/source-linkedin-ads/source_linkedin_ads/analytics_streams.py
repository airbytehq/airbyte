#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional
from urllib.parse import urlencode

import pendulum
import requests
from airbyte_cdk.sources.streams.core import package_name_from_class
from airbyte_cdk.sources.utils import casing
from airbyte_cdk.sources.utils.schema_helpers import ResourceSchemaLoader
from airbyte_protocol.models import SyncMode
from source_linkedin_ads.streams import Campaigns, Creatives, IncrementalLinkedinAdsStream

from .utils import get_parent_stream_values, transform_data

# Number of days ahead for date slices, from start date.
WINDOW_IN_DAYS = 30
# List of Reporting Metrics fields available for fetch
ANALYTICS_FIELDS_V2: List = [
    "actionClicks",
    "adUnitClicks",
    "approximateUniqueImpressions",
    "cardClicks",
    "cardImpressions",
    "clicks",
    "commentLikes",
    "comments",
    "companyPageClicks",
    "conversionValueInLocalCurrency",
    "costInLocalCurrency",
    "costInUsd",
    "dateRange",
    "documentCompletions",
    "documentFirstQuartileCompletions",
    "documentMidpointCompletions",
    "documentThirdQuartileCompletions",
    "downloadClicks",
    "externalWebsiteConversions",
    "externalWebsitePostClickConversions",
    "externalWebsitePostViewConversions",
    "follows",
    "fullScreenPlays",
    "impressions",
    "jobApplications",
    "jobApplyClicks",
    "landingPageClicks",
    "leadGenerationMailContactInfoShares",
    "leadGenerationMailInterestedClicks",
    "likes",
    "oneClickLeadFormOpens",
    "oneClickLeads",
    "opens",
    "otherEngagements",
    "pivotValues",
    "postClickJobApplications",
    "postClickJobApplyClicks",
    "postClickRegistrations",
    "postViewJobApplications",
    "postViewJobApplyClicks",
    "postViewRegistrations",
    "reactions",
    "registrations",
    "sends",
    "shares",
    "talentLeads",
    "textUrlClicks",
    "totalEngagements",
    "validWorkEmailLeads",
    "videoCompletions",
    "videoFirstQuartileCompletions",
    "videoMidpointCompletions",
    "videoStarts",
    "videoThirdQuartileCompletions",
    "videoViews",
    "viralCardClicks",
    "viralCardImpressions",
    "viralClicks",
    "viralCommentLikes",
    "viralComments",
    "viralCompanyPageClicks",
    "viralDocumentCompletions",
    "viralDocumentFirstQuartileCompletions",
    "viralDocumentMidpointCompletions",
    "viralDocumentThirdQuartileCompletions",
    "viralDownloadClicks",
    "viralExternalWebsiteConversions",
    "viralExternalWebsitePostClickConversions",
    "viralExternalWebsitePostViewConversions",
    "viralFollows",
    "viralFullScreenPlays",
    "viralImpressions",
    "viralJobApplications",
    "viralJobApplyClicks",
    "viralLandingPageClicks",
    "viralLikes",
    "viralOneClickLeadFormOpens",
    "viralOneClickLeads",
    "viralOtherEngagements",
    "viralPostClickJobApplications",
    "viralPostClickJobApplyClicks",
    "viralPostClickRegistrations",
    "viralPostViewJobApplications",
    "viralPostViewJobApplyClicks",
    "viralPostViewRegistrations",
    "viralReactions",
    "viralRegistrations",
    "viralShares",
    "viralTotalEngagements",
    "viralVideoCompletions",
    "viralVideoFirstQuartileCompletions",
    "viralVideoMidpointCompletions",
    "viralVideoStarts",
    "viralVideoThirdQuartileCompletions",
    "viralVideoViews",
]


class LinkedInAdsAnalyticsStream(IncrementalLinkedinAdsStream, ABC):
    """
    AdAnalytics Streams more info:
    https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads-reporting/ads-reporting?tabs=curl&view=li-lms-2023-05#analytics-finder
    """

    endpoint = "adAnalytics"
    # For Analytics streams, the primary_key is the entity of the pivot [Campaign URN, Creative URN, etc.] + `end_date`
    primary_key = ["string_of_pivot_values", "end_date"]
    cursor_field = "end_date"
    records_limit = 15000
    FIELDS_CHUNK_SIZE = 18

    def get_json_schema(self) -> Mapping[str, Any]:
        schema = ResourceSchemaLoader(package_name_from_class(self.__class__)).get_schema("ad_analytics")
        schema["properties"].update({self.search_param_value: {"type": ["null", "string"]}})
        return schema

    def __init__(self, name: str = None, pivot_by: str = None, time_granularity: str = None, **kwargs):
        self.user_stream_name = name
        if pivot_by:
            self.pivot_by = pivot_by
        if time_granularity:
            self.time_granularity = time_granularity
        super().__init__(**kwargs)

    @property
    @abstractmethod
    def search_param(self) -> str:
        """
        :return: Search parameters for the request
        """

    @property
    @abstractmethod
    def search_param_value(self) -> str:
        """
        :return: Name field to filter by
        """

    @property
    @abstractmethod
    def parent_values_map(self) -> Mapping[str, str]:
        """
        :return: Mapping for parent child relation
        """

    @property
    def name(self) -> str:
        """We override the stream name to let the user change it via configuration."""
        name = self.user_stream_name or self.__class__.__name__
        return casing.camel_to_snake(name)

    @property
    def base_analytics_params(self) -> MutableMapping[str, Any]:
        """Define the base parameters for analytics streams"""
        return {"q": "analytics", "pivot": f"(value:{self.pivot_by})", "timeGranularity": f"(value:{self.time_granularity})"}

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        headers = super().request_headers(stream_state, stream_slice, next_page_token)
        return headers | {"X-Restli-Protocol-Version": "2.0.0"}

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = self.base_analytics_params
        params.update(**self.update_analytics_params(stream_slice))
        params[self.search_param] = f"List(urn%3Ali%3A{self.search_param_value}%3A{self.get_primary_key_from_slice(stream_slice)})"
        return urlencode(params, safe="():,%")

    @staticmethod
    def update_analytics_params(stream_slice: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Produces the date range parameters from input stream_slice
        """
        date_range = stream_slice["dateRange"]
        return {
            "dateRange": f"(start:(year:{date_range['start.year']},month:{date_range['start.month']},day:{date_range['start.day']}),"
            f"end:(year:{date_range['end.year']},month:{date_range['end.month']},day:{date_range['end.day']}))",
            # Chunk of fields
            "fields": stream_slice["fields"],
        }

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        Pagination is not supported
        (See Restrictions: https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads-reporting/ads-reporting?view=li-lms-2023-09&tabs=http#restrictions)
        """
        parsed_response = response.json()
        is_elements_less_than_limit = len(parsed_response.get("elements")) < self.records_limit

        # Note: The API might return fewer records than requested within the limits during pagination.
        # This behavior is documented at: https://github.com/airbytehq/airbyte/issues/34164
        paging_params = parsed_response.get("paging", {})
        is_end_of_records = (
            paging_params["total"] - paging_params["start"] <= self.records_limit
            if all(param in paging_params for param in ("total", "start"))
            else True
        )

        if is_elements_less_than_limit and is_end_of_records:
            return None
        raise Exception(
            f"Limit {self.records_limit} elements exceeded. "
            f"Try to request your data in more granular pieces. "
            f"(For example switch `Time Granularity` from MONTHLY to DAILY)"
        )

    def get_primary_key_from_slice(self, stream_slice) -> str:
        return stream_slice.get(self.primary_slice_key)

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: Optional[List[str]] = None, stream_state: Optional[Mapping[str, Any]] = None
    ) -> Iterable[Optional[Mapping[str, List[Mapping[str, Any]]]]]:
        """
        LinkedIn has a max of 20 fields per request. We make chunks by size of 19 fields to have the `dateRange` be included as well.
        https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads-reporting/ads-reporting?view=li-lms-2023-05&tabs=http#requesting-specific-metrics-in-the-analytics-finder

        :param sync_mode:
        :param cursor_field:
        :param stream_state:
        :return: An iterable of dictionaries, each containing a single key 'field_date_chunks'. The value under 'field_date_chunks' is
        a list of dictionaries where each dictionary represents a slice of data defined by a specific date range and chunked fields.

        Example of returned data:
        {
            'field_date_chunks': [
                {
                    'campaign_id': 123,
                    'fields': 'field_1,field_2,dateRange',
                    'dateRange': {
                        'start.day': 1, 'start.month': 1, 'start.year': 2020,
                        'end.day': 30, 'end.month': 1, 'end.year': 2020
                    }
                },
                {
                    'campaign_id': 123,
                    'fields': 'field_3,field_4,dateRange',
                    'dateRange': {
                        'start.day': 1, 'start.month': 1, 'start.year': 2020,
                        'end.day': 30, 'end.month': 1, 'end.year': 2020
                    }
                }
            ]
        }
        """
        parent_stream = self.parent_stream(config=self.config)
        stream_state = stream_state or {self.cursor_field: self.config.get("start_date")}
        for record in parent_stream.read_records(sync_mode=sync_mode):
            base_slice = get_parent_stream_values(record, self.parent_values_map)
            for date_slice in self.get_date_slices(stream_state.get(self.cursor_field), self.config.get("end_date")):
                date_slice_with_fields: List = []
                for fields_set in self.chunk_analytics_fields():
                    base_slice["fields"] = ",".join(fields_set)
                    date_slice_with_fields.append(base_slice | date_slice)
                yield {"field_date_chunks": date_slice_with_fields}

    @staticmethod
    def get_date_slices(start_date: str, end_date: str = None, window_in_days: int = WINDOW_IN_DAYS) -> Iterable[Mapping[str, Any]]:
        """
        Produces date slices from start_date to end_date (if specified),
        otherwise end_date will be present time.
        """
        start = pendulum.parse(start_date)
        end = pendulum.parse(end_date) if end_date else pendulum.now()
        date_slices = []
        while start < end:
            slice_end_date = start.add(days=window_in_days)
            date_slice = {
                "start.day": start.day,
                "start.month": start.month,
                "start.year": start.year,
                "end.day": slice_end_date.day,
                "end.month": slice_end_date.month,
                "end.year": slice_end_date.year,
            }
            date_slices.append({"dateRange": date_slice})
            start = slice_end_date
        yield from date_slices

    @staticmethod
    def chunk_analytics_fields(
        fields: List = ANALYTICS_FIELDS_V2,
        fields_chunk_size: int = FIELDS_CHUNK_SIZE,
    ) -> Iterable[List]:
        """
        Chunks the list of available fields into the chunks of equal size.
        """
        # Make chunks
        chunks = list((fields[f : f + fields_chunk_size] for f in range(0, len(fields), fields_chunk_size)))
        # Make sure base_fields are within the chunks
        for chunk in chunks:
            if "dateRange" not in chunk:
                chunk.append("dateRange")
            if "pivotValues" not in chunk:
                chunk.append("pivotValues")
        yield from chunks

    def read_records(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs
    ) -> Iterable[Mapping[str, Any]]:
        merged_records = defaultdict(dict)
        for field_slice in stream_slice.get("field_date_chunks", []):
            for rec in super().read_records(stream_slice=field_slice, **kwargs):
                merged_records[f"{rec[self.cursor_field]}-{rec['pivotValues']}"].update(rec)
        yield from merged_records.values()

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        We need to get out the nested complex data structures for further normalization, so the transform_data method is applied.
        """
        for rec in transform_data(response.json().get("elements")):
            yield rec | {self.search_param_value: self.get_primary_key_from_slice(kwargs.get("stream_slice")), "pivot": self.pivot_by}


class AdCampaignAnalytics(LinkedInAdsAnalyticsStream):
    """
    Campaign Analytics stream.
    """

    endpoint = "adAnalytics"

    parent_stream = Campaigns
    parent_values_map = {"campaign_id": "id"}
    search_param = "campaigns"
    search_param_value = "sponsoredCampaign"
    pivot_by = "CAMPAIGN"
    time_granularity = "DAILY"


class AdCreativeAnalytics(LinkedInAdsAnalyticsStream):
    """
    Creative Analytics stream.
    """

    parent_stream = Creatives
    parent_values_map = {"creative_id": "id"}
    search_param = "creatives"
    search_param_value = "sponsoredCreative"
    pivot_by = "CREATIVE"
    time_granularity = "DAILY"

    def get_primary_key_from_slice(self, stream_slice) -> str:
        creative_id = stream_slice.get(self.primary_slice_key).split(":")[-1]
        return creative_id


class AdImpressionDeviceAnalytics(AdCampaignAnalytics):
    pivot_by = "IMPRESSION_DEVICE_TYPE"


class AdMemberCompanySizeAnalytics(AdCampaignAnalytics):
    pivot_by = "MEMBER_COMPANY_SIZE"


class AdMemberIndustryAnalytics(AdCampaignAnalytics):
    pivot_by = "MEMBER_INDUSTRY"


class AdMemberSeniorityAnalytics(AdCampaignAnalytics):
    pivot_by = "MEMBER_SENIORITY"


class AdMemberJobTitleAnalytics(AdCampaignAnalytics):
    pivot_by = "MEMBER_JOB_TITLE"


class AdMemberJobFunctionAnalytics(AdCampaignAnalytics):
    pivot_by = "MEMBER_JOB_FUNCTION"


class AdMemberCountryAnalytics(AdCampaignAnalytics):
    pivot_by = "MEMBER_COUNTRY_V2"


class AdMemberRegionAnalytics(AdCampaignAnalytics):
    pivot_by = "MEMBER_REGION_V2"


class AdMemberCompanyAnalytics(AdCampaignAnalytics):
    pivot_by = "MEMBER_COMPANY"
