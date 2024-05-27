# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from airbyte_cdk.sources.declarative.requesters import HttpRequester
from airbyte_cdk.sources.declarative.requesters.request_options.interpolated_request_options_provider import (
    InterpolatedRequestOptionsProvider,
    RequestInput,
)
from dataclasses import dataclass
from typing import Any, Mapping, Optional, List
from urllib.parse import urljoin
import pendulum
import requests
from airbyte_cdk.sources.declarative.requesters.request_options.interpolated_request_options_provider import (
    InterpolatedRequestOptionsProvider,
)
from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException, RequestBodyException, UserDefinedBackoffException
from airbyte_cdk.sources.streams.http.http import BODY_REQUEST_METHODS
from urllib.parse import urlencode
import datetime
from dataclasses import InitVar, dataclass, field
from typing import Any, Callable, Iterable, List, Mapping, MutableMapping, Optional, Union
from airbyte_cdk.sources.declarative.incremental import DatetimeBasedCursor
from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage, Level, Type
from airbyte_cdk.sources.declarative.datetime.datetime_parser import DatetimeParser
from airbyte_cdk.sources.declarative.datetime.min_max_datetime import MinMaxDatetime
from airbyte_cdk.sources.declarative.incremental.declarative_cursor import DeclarativeCursor
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.interpolation.jinja import JinjaInterpolation
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption, RequestOptionType
from airbyte_cdk.sources.message import MessageRepository
from airbyte_cdk.sources.types import Config, Record, StreamSlice, StreamState
from isodate import Duration, parse_duration

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
FIELDS_CHUNK_SIZE = 18


@dataclass
class SafeEncodeHttpRequester(HttpRequester):
    """
    This custom component safely validates query parameters, ignoring the symbols ():,% for UTF-8 encoding.

    Attributes:
        request_body_json: Optional JSON body for the request.
        request_headers: Optional headers for the request.
        request_parameters: Optional parameters for the request.
        request_body_data: Optional data body for the request.
    """
    request_body_json: Optional[RequestInput] = None
    request_headers: Optional[RequestInput] = None
    request_parameters: Optional[RequestInput] = None
    request_body_data: Optional[RequestInput] = None

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self.request_options_provider = InterpolatedRequestOptionsProvider(
            request_body_data=self.request_body_data,
            request_body_json=self.request_body_json,
            request_headers=self.request_headers,
            request_parameters=self.request_parameters,
            config=self.config,
            parameters=parameters or {},
        )
        super().__post_init__(parameters)

    def _create_prepared_request(
            self,
            path: str,
            headers: Optional[Mapping[str, str]] = None,
            params: Optional[Mapping[str, Any]] = None,
            json: Any = None,
            data: Any = None,
    ) -> requests.PreparedRequest:
        url = urljoin(self.get_url_base(), path)
        http_method = str(self._http_method.value)
        query_params = self.deduplicate_query_params(url, params)
        query_params = urlencode(query_params, safe="():,%")
        args = {"method": http_method, "url": url, "headers": headers, "params": query_params}
        if http_method.upper() in BODY_REQUEST_METHODS:
            if json and data:
                raise RequestBodyException(
                    "At the same time only one of the 'request_body_data' and 'request_body_json' functions can return data"
                )
            elif json:
                args["json"] = json
            elif data:
                args["data"] = data

        return self._session.prepare_request(requests.Request(**args))


@dataclass
class AnalyticsDatetimeBasedCursor(DatetimeBasedCursor):

    @staticmethod
    def chunk_analytics_fields(
            fields: List = ANALYTICS_FIELDS_V2,
            fields_chunk_size: int = FIELDS_CHUNK_SIZE,
    ) -> Iterable[List]:
        """
        Chunks the list of available fields into the chunks of equal size.
        """
        # Make chunks
        chunks = list((fields[f: f + fields_chunk_size] for f in range(0, len(fields), fields_chunk_size)))
        # Make sure base_fields are within the chunks
        for chunk in chunks:
            if "dateRange" not in chunk:
                chunk.append("dateRange")
            if "pivotValues" not in chunk:
                chunk.append("pivotValues")
        yield from chunks

    def _partition_daterange(
            self, start: datetime.datetime, end: datetime.datetime, step: Union[datetime.timedelta, Duration]
    ) -> List[StreamSlice]:
        dates = []

        while start <= end:
            next_start = self._evaluate_next_start_date_safely(start, step)
            end_date = self._get_date(next_start - self._cursor_granularity, end, min)
            for fields_set in self.chunk_analytics_fields():
                date_range = {
                    "start.day": start.day,
                    "start.month": start.month,
                    "start.year": start.year,
                    "end.day": end_date.day,
                    "end.month": end_date.month,
                    "end.year": end_date.year,
                }

                fields = ",".join(fields_set)
                dates.append(
                    StreamSlice(
                        partition={}, cursor_slice={"fields": fields, **date_range}
                    )
                )
            start = next_start
        return dates
