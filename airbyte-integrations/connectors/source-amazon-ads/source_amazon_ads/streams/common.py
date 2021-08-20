#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import json
from abc import ABC, abstractmethod
from http import HTTPStatus
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

import requests
from airbyte_cdk.sources.streams.core import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from pydantic import BaseModel, ValidationError
from source_amazon_ads.schemas import CatalogModel
from source_amazon_ads.schemas.profile import Profile

URL_BASE = "https://advertising-api.amazon.com/"

"""
This class hierarchy may seem overcomplicated so here is a visualization of
class to provide explanation why it had been done in this way.

airbyte_cdk.sources.streams.core.Stream
└── BasicAmazonAdsStream
    ├── airbyte_cdk.sources.streams.http.HttpStream
    │   └── AmazonAdsStream
    │       ├── Profiles
    │       └── SubProfilesStream
    │           └── PaginationStream
    │               ├── SponsoredDisplayAdGroups
    │               ├── SponsoredDisplayCampaigns
    │               ├── SponsoredDisplayProductAds
    │               ├── SponsoredDisplayTargetings
    │               ├── SponsoredProductAdGroups
    │               ├── SponsoredProductAds
    │               ├── SponsoredProductCampaigns
    │               ├── SponsoredProductKeywords
    │               ├── SponsoredProductNegativeKeywords
    │               ├── SponsoredProductTargetings
    │               ├── SponsoredBrandsCampaigns
    │               ├── SponsoredBrandsAdGroups
    │               ├── SponsoredBrandsKeywords
    │               ├── SponsoredDisplayReportStream
    │               ├── SponsoredProductsReportStream
    │               └── SponsoredBrandsReportStream
    └── ReportStream
        ├── SponsoredBrandsReportStream
        ├── SponsoredDisplayReportStream
        └── SponsoredProductsReportStream

BasicAmazonAdsStream is base class inherited from CDK's Stream class and used
for storing list of profiles that later be used by all the streams to get
profile id. Also it stores pydantic model and API url for requests.

AmazonAdsStream is Http based class, it used for making request that could be
accomlished by single http call (any but report streams). Also in contains
transform method to modify output data (see transform method comment).

SubProfilesStream is subclass for http streams to perform read_records from
basic class for EACH profile from self._profiles list.

PaginationStream class implement Amazon Ads API pagintaion for all requests.
This is base class for all the sync http streams that used by source.

ReportStream (It implemented on report_stream.py file) is subclass for async
report streams. This is not standard http stream and used for generating
reports for profiles from BasicAmazonAdsStream _profiles list.

"""


class ErrorResponse(BaseModel):
    code: str
    details: str
    requestId: str


class BasicAmazonAdsStream(Stream, ABC):
    """
    Base class for all Amazon Ads streams.
    """

    def __init__(self, config, profiles: List[Profile] = None):
        self._profiles = profiles or []
        self._client_id = config.client_id
        self._url = config.host or URL_BASE

    @property
    @abstractmethod
    def model(self) -> CatalogModel:
        """
        Pydantic model to represent json schema
        """

    def get_json_schema(self):
        return self.model.schema()


# Basic full refresh stream
class AmazonAdsStream(HttpStream, BasicAmazonAdsStream):
    """
    Class for getting data from streams that based on single http request.
    """

    # List of properties that used by transform method to convert "object"
    # subtype with complex dict to plan string.
    flatten_properties = []

    def __init__(self, config, *args, profiles: List[Profile] = None, **kwargs):
        BasicAmazonAdsStream.__init__(self, config, profiles=profiles)
        HttpStream.__init__(self, *args, **kwargs)

    @property
    def url_base(self):
        return self._url

    def transform(self, record: dict):
        """
        Convert properties that listed on flatten_properties variable from dict
        to plain string. We need it to not overcomplicate catalog model with
        objects containing internal information and unlikely to be used for analytics.
        """
        for prop in self.flatten_properties:
            if prop in record:
                record[prop] = json.dumps(record[prop])
        return record

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_headers(self, *args, **kvargs) -> MutableMapping[str, Any]:
        return {"Amazon-Advertising-API-ClientId": self._client_id}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an object representing single record in the response
        """
        yield from response.json() if response else []

    def _send_request(self, request: requests.PreparedRequest, request_kwargs: Mapping[str, Any]) -> requests.Response:
        """
        Override private HttpStream method to handle Amazon API error
        responses. There could be 2 types or errors: One that generated by
        servers itself, it has response with JSON like this:
        '''
        {
            "message": "<error message>"
        }
        '''
        and errors that desribed on Amazon Advertising API docs and have this format:
        '''
        {
           "code": "<error code>",
           "details": "<error message>",
           "requestId": "<request id>"
        }

        '''
        First type of error is crititcal so we can't proceed further and
        generate an exception and for the second type there is only warning
        dispalyed and we can move to the next stream.
        """
        try:
            return super()._send_request(request, request_kwargs)
        except requests.exceptions.HTTPError as http_exception:
            response = http_exception.response
            if response.status_code == HTTPStatus.FORBIDDEN:
                try:
                    resp = ErrorResponse.parse_raw(response.text)
                    self.logger.warn(
                        f"Unexpected error {resp.code} when processing request {request.url} for {request.headers['Amazon-Advertising-API-Scope']} profile: {resp.details}"
                    )
                except ValidationError:
                    raise http_exception
            else:
                raise http_exception


class SubProfilesStream(AmazonAdsStream):
    """
    Stream for getting resources based on context set by previous stream.
    """

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        for record in super().parse_response(response, **kwargs):
            yield self.transform(record)

    def read_records(self, *args, **kvargs) -> Iterable[Mapping[str, Any]]:
        """
        Iterate through self._profiles list and send read all records for each profile.
        """
        for profile in self._profiles:
            self._current_profile_id = profile.profileId
            yield from super().read_records(*args, **kvargs)

    def request_headers(self, *args, **kvargs) -> MutableMapping[str, Any]:
        headers = super().request_headers(*args, **kvargs)
        headers["Amazon-Advertising-API-Scope"] = str(self._current_profile_id)
        return headers


class PaginationStream(SubProfilesStream):
    """
    Stream for getting resources with pagination support.
    """

    page_size = 100

    def __init__(self, *args, **kvargs):
        self._current_offset = 0
        super().__init__(*args, **kvargs)

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
