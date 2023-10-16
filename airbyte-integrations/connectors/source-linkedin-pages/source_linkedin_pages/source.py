#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib.parse import urlencode

import pendulum
import requests
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import Oauth2Authenticator, TokenAuthenticator
from source_linkedin_pages.utils import build_share_statistics_parameter, build_share_statistics_parameters, flatten_social_metadata_record, parse_post_media_content

LINKEDIN_VERSION_API = "202309"


class LinkedinPagesStream(HttpStream, ABC):

    url_base = "https://api.linkedin.com/rest/"
    primary_key = None
    endpoint = None

    def __init__(self, config):
        super().__init__(authenticator=config.get("authenticator"))
        self.config = config

    @property
    def org(self):
        """Property to return the user Organization Id from input"""
        return self.config.get("org_id")

    def path(self, **kwargs) -> str:
        """Returns the API endpoint path for stream, from `endpoint` class attribute."""
        return self.endpoint

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def parse_response(
        self, response: requests.Response, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None
    ) -> Iterable[Mapping]:
        return [response.json()]

    def should_retry(self, response: requests.Response) -> bool:
        if response.status_code == 429:
            error_message = (
                f"Stream {self.name}: LinkedIn API requests are rate limited. "
                f"Rate limits specify the maximum number of API calls that can be made in a 24 hour period. "
                f"These limits reset at midnight UTC every day. "
                f"You can find more information here https://docs.airbyte.com/integrations/sources/linkedin-pages. "
                f"Also quotas and usage are here: https://www.linkedin.com/developers/apps."
            )
            self.logger.error(error_message)
        return super().should_retry(response)

    def request_headers(
        self,
        stream_state: Optional[Mapping[str, Any]],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return {"Linkedin-Version": LINKEDIN_VERSION_API}

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[MutableMapping[str, Any]]:
        return None

    @property
    def raise_on_http_errors(self) -> bool:
        """
        Override if needed. If set to False, allows opting-out of raising HTTP code exception.
        """
        return True

    @property
    def _start_date_epoch_ms(self):
        """Property to return the epoch time in ms for 365 days ago as that's the maximum the API allows"""
        now = pendulum.now()
        return round(now.subtract(days=365).timestamp() * 1000)


class Organizations(LinkedinPagesStream):

    def path(self, stream_state: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:

        path = f"organizations/{self.org}"
        return path


class OrganizationFollowers(LinkedinPagesStream):

    def path(self, stream_state: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        path = f"networkSizes/urn:li:organization:{self.org}"
        return path

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = {
            "edgeType": "COMPANY_FOLLOWED_BY_MEMBER",
        }
        return params

    def parse_response(
        self, response: requests.Response, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None
    ) -> Iterable[Mapping]:
        record = response.json()
        record["organizationId"] = self.org
        yield record


class OrganizationStatistics(LinkedinPagesStream):
    """
    Retrieve Daily statistics for the organization
    https://learn.microsoft.com/en-us/linkedin/marketing/integrations/community-management/organizations/share-statistics?view=li-lms-2023-09&tabs=http#retrieve-time-bound-share-statistics
    """

    endpoint = "organizationalEntityShareStatistics"

    """ Disabling Pagination as per [MVP-2943] """
    # records_limit = 10
    # def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
    #     parsed_response = response.json()
    #     print(f"(OrganizationStatistics.next_page_token) -> parsed_response: {parsed_response}")
    #     if len(parsed_response.get("elements")) < self.records_limit:
    #         return None
    #     return {"start": parsed_response.get("paging").get("start") + self.records_limit}

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = {
            "q": "organizationalEntity",
            "organizationalEntity": f"urn:li:organization:{self.org}",
            "timeIntervals.timeGranularityType": "DAY",
            "timeIntervals.timeRange.start": self._start_date_epoch_ms,
        }
        if next_page_token:
            params.update(**next_page_token)
        return params

    def parse_response(
        self, response: requests.Response, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None
    ) -> Iterable[Mapping]:
        yield from response.json().get("elements")


class Posts(LinkedinPagesStream):
    records_limit = 10

    def path(self, stream_state: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        path = f"posts"
        return path

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        parsed_response = response.json()
        if len(parsed_response.get("elements")) < self.records_limit:
            return None
        return {"start": parsed_response.get("paging").get("start") + self.records_limit}

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = {
            "q": "author",
            "author": f"urn:li:organization:{self.org}",
        }
        if next_page_token:
            params.update(**next_page_token)
        return params

    def parse_response(
        self, response: requests.Response, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None
    ) -> Iterable[Mapping]:
        yield from response.json().get("elements")


class ShareStatisticsDaily(LinkedinPagesStream):
    """
    Retrieve Daily Statistics for shares & posts
    https://learn.microsoft.com/en-us/linkedin/marketing/integrations/community-management/organizations/share-statistics?view=li-lms-2023-09&tabs=http#retrieve-statistics-for-specific-shares
    """
    endpoint = "organizationalEntityShareStatistics"
    parent_stream = Posts

    def __init__(self, config):
        super().__init__(config)
        self.request_param_builder_map = None

    @property
    def raise_on_http_errors(self) -> bool:
        """
        Don't raise the error as we expect it to fail with no build parameters
        """
        return True if self.request_param_builder_map else False

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = {
            "q": "organizationalEntity",
            "organizationalEntity": f"urn:li:organization:{self.org}",
            "timeIntervals.timeGranularityType": "DAY",
            "timeIntervals.timeRange.start": self._start_date_epoch_ms,
        }
        if self.request_param_builder_map:
            params = params | self.request_param_builder_map
        if next_page_token:
            params.update(**next_page_token)
        return urlencode(params, safe="():,%[]")

    def parse_response(
        self, response: requests.Response, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None
    ) -> Iterable[Mapping]:
        yield from response.json().get("elements")

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        parent_stream = self.parent_stream(config=self.config)
        parent_records = parent_stream.read_records(sync_mode, cursor_field, stream_slice, stream_state)
        for parent_record in parent_records:
            self.request_param_builder_map = build_share_statistics_parameter(record_id=parent_record["id"])

            if self.request_param_builder_map:
                records = super().read_records(sync_mode, cursor_field, stream_slice, stream_state)
                yield from records


class SocialMetadata(LinkedinPagesStream):
    """
    Batch retrieve a summary of social metadata
    https://learn.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares/social-metadata-api?view=li-lms-unversioned&tabs=http#batch-get-a-summary-of-social-metadata    """
    endpoint = "socialMetadata"
    parent_stream = Posts

    @property
    def raise_on_http_errors(self) -> bool:
        """
        Don't raise the error as we expect it to fail with no build parameters
        """
        return True if self.build_param_ids() else False

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = {}
        return params | self.build_param_ids()

    def parse_response(
        self, response: requests.Response, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None
    ) -> Iterable[Mapping]:
        results = response.json().get("results", {}).values()
        for record in results:
            yield flatten_social_metadata_record(record)

    def build_param_ids(self) -> Mapping[str, str]:
        """
        Parameter format required for specific posts/shares is an index iterated list of ids:
         Post: `ids[0]=urn:li:ugcPost:10000`
         Share: `ids[1]=urn:li:share:100000`
        """
        parent_stream = self.parent_stream(config=self.config)

        ids = [record["id"] for record in parent_stream.read_records(sync_mode=SyncMode.full_refresh)]
        return {f"ids[{x}]": i for x, i in enumerate(ids)}


class Images(LinkedinPagesStream):
    """
    Batch retrieve a summary of images
    https://learn.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares/social-metadata-api?view=li-lms-unversioned&tabs=http#batch-get-a-summary-of-social-metadata    """
    endpoint = "images"
    parent_stream = Posts

    @property
    def raise_on_http_errors(self) -> bool:
        """
        Don't raise the error as we expect it to fail with no build parameters
        """
        return True if self.build_param_ids() else False

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = {}
        return params | self.build_param_ids()

    def parse_response(
        self, response: requests.Response, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None
    ) -> Iterable[Mapping]:
        results = list(response.json().get("results", {}).values())
        yield from results

    def build_param_ids(self) -> Mapping[str, str]:
        """
        Parameter format required for specific images is an index iterated list of ids:
         `ids[0]=urn:li:image:10000&ids[1]=urn:li:image:10000`
        """
        parent_stream = self.parent_stream(config=self.config)
        images_ids = []

        for record in parent_stream.read_records(sync_mode=SyncMode.full_refresh):
            if record.get("distribution", {}).get("feedDistribution") == "MAIN_FEED":
                if record.get("content"):
                    images_ids.extend(parse_post_media_content(record["content"], media_type="image"))
        return {f"ids[{x}]": i for x, i in enumerate(images_ids)}


class Documents(LinkedinPagesStream):
    """
    Batch retrieve a summary of videos
    https://learn.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares/documents-api?view=li-lms-2023-09&tabs=http
    """
    endpoint = "documents"
    parent_stream = Posts

    @property
    def raise_on_http_errors(self) -> bool:
        """
        Don't raise the error as we expect it to fail with no build parameters
        """
        return True if self.build_param_ids() else False

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = {}
        return params | self.build_param_ids()

    def parse_response(
        self, response: requests.Response, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None
    ) -> Iterable[Mapping]:
        results = list(response.json().get("results", {}).values())
        yield from results

    def build_param_ids(self) -> Mapping[str, str]:
        """
        Parameter format required for specific images is an index iterated list of ids:
         `ids[0]=urn:li:document:10000&ids[1]=urn:li:video:10000`
        """
        parent_stream = self.parent_stream(config=self.config)
        document_ids = []

        for record in parent_stream.read_records(sync_mode=SyncMode.full_refresh):
            if record.get("distribution", {}).get("feedDistribution") == "MAIN_FEED":
                if record.get("content"):
                    document_ids.extend(parse_post_media_content(record["content"], media_type="document"))
        return {f"ids[{x}]": i for x, i in enumerate(document_ids)}


class Videos(LinkedinPagesStream):
    """
    Batch retrieve a summary of videos
    https://learn.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares/social-metadata-api?view=li-lms-unversioned&tabs=http#batch-get-a-summary-of-social-metadata    """
    endpoint = "videos"
    parent_stream = Posts

    @property
    def raise_on_http_errors(self) -> bool:
        """
        Don't raise the error as we expect it to fail with no build parameters
        """
        return True if self.build_param_ids() else False

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = {}
        return params | self.build_param_ids()

    def parse_response(
        self, response: requests.Response, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None
    ) -> Iterable[Mapping]:
        results = list(response.json().get("results", {}).values())
        yield from results

    def build_param_ids(self) -> Mapping[str, str]:
        """
        Parameter format required for specific videos is an index iterated list of ids:
         `ids[0]=urn:li:video:10000&ids[1]=urn:li:video:10000`
        """
        parent_stream = self.parent_stream(config=self.config)
        video_ids = []

        for record in parent_stream.read_records(sync_mode=SyncMode.full_refresh):
            if record.get("distribution", {}).get("feedDistribution") == "MAIN_FEED":
                if record.get("content"):
                    video_ids.extend(parse_post_media_content(record["content"], media_type="video"))
        return {f"ids[{x}]": i for x, i in enumerate(video_ids)}


class SourceLinkedinPages(AbstractSource):
    """
    Abstract Source inheritance, provides:
    - implementation for `check` connector's connectivity
    - implementation to call each stream with it's input parameters.
    """

    @classmethod
    def get_authenticator(cls, config: Mapping[str, Any]) -> TokenAuthenticator:
        """
        Validate input parameters and generate a necessary Authentication object
        This connectors support 2 auth methods:
        1) direct access token with TTL = 2 months
        2) refresh token (TTL = 1 year) which can be converted to access tokens
           Every new refresh revokes all previous access tokens q
        """
        auth_method = config.get("credentials", {}).get("auth_method")
        if not auth_method or auth_method == "access_token":
            # support of backward compatibility with old exists configs
            access_token = config["credentials"]["access_token"] if auth_method else config["access_token"]
            return TokenAuthenticator(token=access_token)
        elif auth_method == "oAuth2.0":
            return Oauth2Authenticator(
                token_refresh_endpoint="https://www.linkedin.com/oauth/v2/accessToken",
                client_id=config["credentials"]["client_id"],
                client_secret=config["credentials"]["client_secret"],
                refresh_token=config["credentials"]["refresh_token"],
            )
        raise Exception("incorrect input parameters")

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        # RUN $ python main.py check --config secrets/config.json

        """
        Testing connection availability for the connector.
        :: for this check method the Customer must have the "r_liteprofile" scope enabled.
        :: more info: https://docs.microsoft.com/linkedin/consumer/integrations/self-serve/sign-in-with-linkedin
        """

        config["authenticator"] = self.get_authenticator(config)
        stream = Organizations(config)
        stream.records_limit = 1
        try:
            next(stream.read_records(sync_mode=SyncMode.full_refresh), None)
            return True, None
        except Exception as e:
            return False, e

        # RUN: $ python main.py read --config secrets/config.json --catalog integration_tests/configured_catalog.json

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config["authenticator"] = self.get_authenticator(config)
        return [
            Organizations(config),
            OrganizationFollowers(config),
            OrganizationStatistics(config),
            Posts(config),
            ShareStatisticsDaily(config),
            SocialMetadata(config),
            Images(config),
            Documents(config),
            Videos(config)
        ]
