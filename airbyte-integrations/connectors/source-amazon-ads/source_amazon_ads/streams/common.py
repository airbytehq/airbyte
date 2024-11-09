#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
from abc import ABC
from http import HTTPStatus
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union

import requests
from airbyte_cdk.sources.declarative.models import FailureType
from airbyte_cdk.sources.streams.core import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.error_handlers import ErrorHandler, ErrorResolution, HttpStatusErrorHandler, ResponseAction
from pydantic.v1 import BaseModel, ValidationError
from source_amazon_ads.constants import URL_MAPPING

"""
This class hierarchy may seem overcomplicated so here is a visualization of
class to provide explanation why it had been done in this way.

airbyte_cdk.sources.streams.core.Stream
└── BasicAmazonAdsStream
    ├── airbyte_cdk.sources.streams.http.HttpStream
    │   └── AmazonAdsStream
    │       ├── Profiles
    │       ├── Portfolios
    │       └── SubProfilesStream
    │           ├── SponsoredDisplayAdGroups
    │           ├── SponsoredDisplayCampaigns
    │           ├── SponsoredDisplayProductAds
    │           ├── SponsoredDisplayTargetings
    │           ├── SponsoredProductsV3
    │           |    ├── SponsoredProductAdGroups
    │           |    ├── SponsoredProductAds
    │           |    ├── SponsoredProductCampaigns
    │           |    ├── SponsoredProductKeywords
    │           |    ├── SponsoredProductNegativeKeywords
    │           |    └── SponsoredProductTargetings
    │           ├── SponsoredBrandsV4
    │           |    ├── SponsoredBrandsCampaigns
    │           |    └── SponsoredBrandsAdGroups
    │           └── SponsoredBrandsKeywords
    └── ReportStream
        ├── SponsoredBrandsV3ReportStream
        ├── SponsoredDisplayReportStream
        └── SponsoredProductsReportStream

BasicAmazonAdsStream is base class inherited from CDK's Stream class and used
for storing list of profiles that later be used by all the streams to get
profile id. Also it stores pydantic model and API url for requests.

AmazonAdsStream is Http based class, it used for making request that could be
accomplished by single http call (any but report streams).

SubProfilesStream is subclass for http streams to perform read_records from
basic class for EACH profile from self._profiles list. Also provides support
for Amazon Ads API pagination. This is base class for all the sync http streams
that used by source.

ReportStream (It implemented on report_stream.py file) is subclass for async
report streams. This is not standard http stream and used for generating
reports for profiles from BasicAmazonAdsStream _profiles list.

"""

LOGGER = logging.getLogger("airbyte")


class ErrorResponse(BaseModel):
    code: str
    details: str
    requestId: Optional[str]


class AmazonAdsErrorHandler(HttpStatusErrorHandler):
    def interpret_response(self, response_or_exception: Optional[Union[requests.Response, Exception]] = None) -> ErrorResolution:

        if response_or_exception.status_code == HTTPStatus.OK:
            return ErrorResolution(ResponseAction.SUCCESS)

        try:
            resp = ErrorResponse.parse_raw(response_or_exception.text)
        except ValidationError:
            return ErrorResolution(
                response_action=ResponseAction.FAIL,
                failure_type=FailureType.system_error,
                error_message=f"Response status code: {response_or_exception.status_code}. Unexpected error. {response_or_exception.text=}",
            )

        LOGGER.warning(
            f"Unexpected error {resp.code} when processing request {response_or_exception.request.url} for "
            f"{response_or_exception.request.headers['Amazon-Advertising-API-Scope']} profile: {resp.details}"
        )

        return ErrorResolution(ResponseAction.SUCCESS)


class BasicAmazonAdsStream(Stream, ABC):
    """
    Base class for all Amazon Ads streams.
    """

    is_resumable = False

    def __init__(self, config: Mapping[str, Any], profiles: List[dict[str, Any]] = None):
        self._profiles = profiles or []
        self._client_id = config["client_id"]
        self._url = URL_MAPPING[config["region"]]


# Basic full refresh stream
class AmazonAdsStream(HttpStream, BasicAmazonAdsStream):
    """
    Class for getting data from streams that based on single http request.
    """

    data_field = ""

    def __init__(self, config: Mapping[str, Any], *args, profiles: List[dict[str, Any]] = None, **kwargs):
        # Each AmazonAdsStream instance are dependant on list of profiles.
        BasicAmazonAdsStream.__init__(self, config, profiles=profiles)
        HttpStream.__init__(self, *args, **kwargs)

    @property
    def url_base(self):
        return self._url

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_headers(self, *args, **kwargs) -> MutableMapping[str, Any]:
        return {"Amazon-Advertising-API-ClientId": self._client_id}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an object representing single record in the response
        """
        if response.status_code == HTTPStatus.OK:
            if self.data_field:
                yield from response.json().get(self.data_field, [])
            else:
                yield from response.json()
            return

        """
        There could be 2 types of errors: One that is generated by
        servers itself, it has JSON response like this:
        '''
        {
            "message": "<error message>"
        }
        '''
        and the errors that are described on Amazon Advertising API docs and have this format:
        '''
        {
           "code": "<error code>",
           "details": "<error message>",
           "requestId": "<request id>"
        }
        '''
        The first type of error is critical so we can't proceed further and
        generate an exception and for the second type there is the only warning
        displayed and we can move to the next stream.
        """

        try:
            resp = ErrorResponse.parse_raw(response.text)
        except ValidationError:
            response.raise_for_status()
            raise Exception(response.text)

        self.logger.warning(
            f"Unexpected error {resp.code} when processing request {response.request.url} for "
            f"{response.request.headers['Amazon-Advertising-API-Scope']} profile: {resp.details}"
        )

    def get_error_handler(self) -> ErrorHandler:
        return AmazonAdsErrorHandler(logger=LOGGER)


class SubProfilesStream(AmazonAdsStream):
    """
    Stream for getting resources with pagination support and getting resources based on list of profiles set by source.
    """

    page_size = 100

    def __init__(self, *args, **kwargs):
        self._current_offset = 0
        super().__init__(*args, **kwargs)

    def next_page_token(self, response: requests.Response) -> Optional[int]:
        if not response:
            return 0
        responses = response.json()
        if len(responses) < self.page_size:
            # This is last page, reset current offset
            self._current_offset = 0
            return 0
        else:
            next_offset = self._current_offset + self.page_size
            self._current_offset = next_offset
            return next_offset

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: int = None,
    ) -> MutableMapping[str, Any]:
        return {
            "startIndex": next_page_token,
            "count": self.page_size,
        }

    def read_records(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        """
        Iterate through self._profiles list and send read all records for each profile.
        """
        for profile in self._profiles:
            self._current_profile_id = profile["profileId"]
            yield from super().read_records(*args, **kwargs)

    def request_headers(self, *args, **kwargs) -> MutableMapping[str, Any]:
        headers = super().request_headers(*args, **kwargs)
        headers["Amazon-Advertising-API-Scope"] = str(self._current_profile_id)
        return headers
