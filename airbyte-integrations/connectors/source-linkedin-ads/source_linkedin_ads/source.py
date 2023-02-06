#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import logging
from abc import ABC, abstractproperty
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib.parse import urlencode

import backoff
import requests
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import Oauth2Authenticator, TokenAuthenticator
from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException

from .analytics import make_analytics_slices, merge_chunks, update_analytics_params
from .utils import get_parent_stream_values, transform_data

logger = logging.getLogger("airbyte")


class LinkedinAdsStream(HttpStream, ABC):
    """
    Basic class provides base functionality for all streams.
    """

    url_base = "https://api.linkedin.com/v2/"
    primary_key = "id"
    records_limit = 500

    def __init__(self, config: Dict):
        super().__init__(authenticator=config.get("authenticator"))
        self.config = config

    @property
    def accounts(self):
        """Property to return the list of the user Account Ids from input"""
        return ",".join(map(str, self.config.get("account_ids")))

    @property
    def availability_strategy(self) -> Optional["AvailabilityStrategy"]:
        return None

    def path(self, **kwargs) -> str:
        """Returns the API endpoint path for stream, from `endpoint` class attribute."""
        return self.endpoint

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        To paginate through results, begin with a start value of 0 and a count value of N.
        To get the next page, set start value to N, while the count value stays the same.
        We have reached the end of the dataset when the response contains fewer elements than the `count` parameter request.
        https://docs.microsoft.com/en-us/linkedin/shared/api-guide/concepts/pagination?context=linkedin/marketing/context
        """
        parsed_response = response.json()
        if len(parsed_response.get("elements")) < self.records_limit:
            return None
        return {"start": parsed_response.get("paging").get("start") + self.records_limit}

    def request_params(
        self, stream_state: Mapping[str, Any], next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        params = {"count": self.records_limit, "q": "search"}
        if next_page_token:
            params.update(**next_page_token)
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        We need to get out the nested complex data structures for further normalisation, so the transform_data method is applied.
        """
        yield from transform_data(response.json().get("elements"))

    def should_retry(self, response: requests.Response) -> bool:
        if response.status_code == 429:
            error_message = (
                f"Stream {self.name}: LinkedIn API requests are rate limited. "
                f"Rate limits specify the maximum number of API calls that can be made in a 24 hour period. "
                f"These limits reset at midnight UTC every day. "
                f"You can find more information here https://docs.airbyte.com/integrations/sources/linkedin-ads. "
                f"Also quotas and usage are here: https://www.linkedin.com/developers/apps."
            )
            self.logger.error(error_message)
        return super().should_retry(response)


class Accounts(LinkedinAdsStream):
    """
    Get Accounts data. More info about LinkedIn Ads / Accounts:
    https://docs.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-accounts?tabs=http
    """

    endpoint = "adAccountsV2"

    def request_headers(self, stream_state: Mapping[str, Any], **kwargs) -> Mapping[str, Any]:
        """
        If account_ids are specified as user's input from configuration,
        we must use MODIFIED header: {'X-RestLi-Protocol-Version': '2.0.0'}
        """
        return {"X-RestLi-Protocol-Version": "2.0.0"} if self.accounts else {}

    def request_params(self, stream_state: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        """
        Override request_params() to have the ability to accept the specific account_ids from user's configuration.
        If we have list of account_ids, we need to make sure that the request_params are encoded correctly,
        We will get HTTP Error 500, if we use standard requests.urlencode methods to parse parameters,
        so the urlencode(..., safe=":(),") is used instead, to keep the values as they are.
        """
        params = super().request_params(stream_state=stream_state, **kwargs)
        if self.accounts:
            params["search"] = f"(id:(values:List({self.accounts})))"
            return urlencode(params, safe=":(),")
        return params


class IncrementalLinkedinAdsStream(LinkedinAdsStream):

    cursor_field = "lastModified"

    @property
    def primary_slice_key(self) -> str:
        """
        Define the main slice_key from `slice_key_value_map`. Always the first element.
        EXAMPLE:
            in : {"k1": "v1", "k2": "v2", ...}
            out : "k1"
        """
        return list(self.parent_values_map.keys())[0]

    @abstractproperty
    def parent_stream(self) -> object:
        """Defines the parrent stream for slicing, the class object should be provided."""

    @property
    def state_checkpoint_interval(self) -> Optional[int]:
        """Define the checkpoint from the records output size."""
        return super().records_limit

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        current_stream_state = {self.cursor_field: self.config.get("start_date")} if not current_stream_state else current_stream_state
        return {self.cursor_field: max(latest_record.get(self.cursor_field), current_stream_state.get(self.cursor_field))}


class LinkedInAdsStreamSlicing(IncrementalLinkedinAdsStream):
    """
    This class stands for provide stream slicing for other dependent streams.
    :: `parent_stream` - the reference to the parent stream class,
        by default it's referenced to the Accounts stream class, as far as majority of streams are using it.
    :: `parent_values_map` - key_value map for stream slices in a format: {<slice_key_name>: <key inside record>}
    :: `search_param` - the query param to pass with request_params
    :: `search_param_value` - the value for `search_param` to pass with request_params
    """

    parent_stream = Accounts
    parent_values_map = {"account_id": "id"}
    # define default additional request params
    search_param = "search.account.values[0]"
    search_param_value = "urn:li:sponsoredAccount:"

    def request_params(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, **kwargs)
        params[self.search_param] = f"{self.search_param_value}{stream_slice.get(self.primary_slice_key)}"
        return params

    def filter_records_newer_than_state(
        self, stream_state: Mapping[str, Any] = None, records_slice: Iterable[Mapping[str, Any]] = None
    ) -> Iterable:
        """For the streams that provide the cursor_field `lastModified`, we filter out the old records."""
        if stream_state:
            for record in records_slice:
                if record[self.cursor_field] >= stream_state.get(self.cursor_field):
                    yield record
        else:
            yield from records_slice

    def read_records(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs
    ) -> Iterable[Mapping[str, Any]]:
        stream_state = stream_state or {}
        parent_stream = self.parent_stream(config=self.config)
        for record in parent_stream.read_records(**kwargs):
            child_stream_slice = super().read_records(stream_slice=get_parent_stream_values(record, self.parent_values_map), **kwargs)
            yield from self.filter_records_newer_than_state(stream_state=stream_state, records_slice=child_stream_slice)


class AccountUsers(LinkedInAdsStreamSlicing):
    """
    Get AccountUsers data using `account_id` slicing. More info about LinkedIn Ads / AccountUsers:
    https://docs.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-account-users?tabs=http
    """

    endpoint = "adAccountUsersV2"
    # Account_users stream doesn't have `id` property, so the "account" is used instead.
    primary_key = "account"
    search_param = "accounts"

    def request_params(self, stream_state: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, **kwargs)
        params["q"] = self.search_param
        return params


class CampaignGroups(LinkedInAdsStreamSlicing):
    """
    Get CampaignGroups data using `account_id` slicing.
    More info about LinkedIn Ads / CampaignGroups:
    https://docs.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-campaign-groups?tabs=http
    """

    endpoint = "adCampaignGroupsV2"


class Campaigns(LinkedInAdsStreamSlicing):
    """
    Get Campaigns data using `account_id` slicing.
    More info about LinkedIn Ads / Campaigns:
    https://docs.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-campaigns?tabs=http
    """

    endpoint = "adCampaignsV2"


class Creatives(LinkedInAdsStreamSlicing):
    """
    Get Creatives data using `campaign_id` slicing.
    More info about LinkedIn Ads / Creatives:
    https://docs.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-creatives?tabs=http
    """

    endpoint = "adCreativesV2"
    parent_stream = Campaigns
    parent_values_map = {"campaign_id": "id"}
    search_param = "search.campaign.values[0]"
    search_param_value = "urn:li:sponsoredCampaign:"


class AdDirectSponsoredContents(LinkedInAdsStreamSlicing):
    """
    Get AdDirectSponsoredContents data using `account_id` slicing.
    More info about LinkedIn Ads / adDirectSponsoredContents:
    https://docs.microsoft.com/en-us/linkedin/marketing/integrations/ads/advertising-targeting/create-and-manage-video?tabs=http#finders
    """

    endpoint = "adDirectSponsoredContents"
    # AdDirectSponsoredContents stream doesn't have `id` property, so the "account" is used instead.
    primary_key = "account"
    parent_values_map = {"account_id": "id", "reference_id": "reference"}
    search_param = "account"

    def request_params(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, **kwargs)
        params["owner"] = stream_slice.get("reference_id")
        params["q"] = self.search_param
        return params

    def read_records(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs
    ) -> Iterable[Mapping[str, Any]]:
        stream_state = stream_state or {}
        parent_stream = self.parent_stream(config=self.config)
        for record in parent_stream.read_records(**kwargs):

            if record.get("reference", "").startswith("urn:li:person"):
                self.logger.warn(
                    f'Skip {record.get("name")} account, ORGANIZATION permissions required, but referenced to PERSON {record.get("reference")}'
                )
                continue

            child_stream_slice = super(LinkedInAdsStreamSlicing, self).read_records(
                stream_slice=get_parent_stream_values(record, self.parent_values_map), **kwargs
            )
            yield from self.filter_records_newer_than_state(stream_state=stream_state, records_slice=child_stream_slice)


class LinkedInAdsAnalyticsStream(IncrementalLinkedinAdsStream):
    """
    AdAnalytics Streams more info:
    https://docs.microsoft.com/en-us/linkedin/marketing/integrations/ads-reporting/ads-reporting?tabs=curl#ad-analytics
    """

    endpoint = "adAnalyticsV2"
    # For Analytics streams the primary_key is the entity of the pivot [Campaign URN, Creative URN, etc] + `end_date`
    primary_key = ["pivotValue", "end_date"]
    cursor_field = "end_date"

    @property
    def base_analytics_params(self) -> MutableMapping[str, Any]:
        """Define the base parameters for analytics streams"""
        return {"q": "analytics", "pivot": self.pivot_by, "timeGranularity": "DAILY"}

    def request_params(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        params = self.base_analytics_params
        params[self.search_param] = f"{self.search_param_value}{stream_slice.get(self.primary_slice_key)}"
        params.update(**update_analytics_params(stream_slice))
        return params

    def read_records(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs
    ) -> Iterable[Mapping[str, Any]]:
        stream_state = stream_state or {self.cursor_field: self.config.get("start_date")}
        parent_stream = self.parent_stream(config=self.config)
        for record in parent_stream.read_records(**kwargs):
            result_chunks = []
            for analytics_slice in make_analytics_slices(
                record, self.parent_values_map, stream_state.get(self.cursor_field), self.config.get("end_date")
            ):
                child_stream_slice = super().read_records(stream_slice=analytics_slice, **kwargs)
                result_chunks.append(child_stream_slice)
            yield from merge_chunks(result_chunks, self.cursor_field)


class AdCampaignAnalytics(LinkedInAdsAnalyticsStream):
    """
    Campaing Analytics stream.
    See the AnalyticsStreamMixin class for more information.
    """

    parent_stream = Campaigns
    parent_values_map = {"campaign_id": "id"}
    search_param = "campaigns[0]"
    search_param_value = "urn:li:sponsoredCampaign:"
    pivot_by = "CAMPAIGN"


class AdCreativeAnalytics(LinkedInAdsAnalyticsStream):
    """
    Creative Analytics stream.
    See the AnalyticsStreamMixin class for more information.
    """

    parent_stream = Creatives
    parent_values_map = {"creative_id": "id"}
    search_param = "creatives[0]"
    search_param_value = "urn:li:sponsoredCreative:"
    pivot_by = "CREATIVE"


class LinkedinAdsOAuth2Authenticator(Oauth2Authenticator):
    @backoff.on_exception(
        backoff.expo,
        DefaultBackoffException,
        on_backoff=lambda details: logger.info(
            f"Caught retryable error after {details['tries']} tries. Waiting {details['wait']} seconds then retrying..."
        ),
        max_time=300,
    )
    def refresh_access_token(self) -> Tuple[str, int]:
        try:
            response = requests.request(
                method="POST",
                url=self.token_refresh_endpoint,
                data=self.get_refresh_request_body(),
                headers=self.get_refresh_access_token_headers(),
            )
            response.raise_for_status()
            response_json = response.json()
            return response_json["access_token"], response_json["expires_in"]
        except requests.exceptions.RequestException as e:
            if e.response.status_code == 429 or e.response.status_code >= 500:
                raise DefaultBackoffException(request=e.response.request, response=e.response)
            raise
        except Exception as e:
            raise Exception(f"Error while refreshing access token: {e}") from e


class SourceLinkedinAds(AbstractSource):
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
        2) refresh token (TTL = 1 year) which can be converted to access tokens,
           Every new refresh revokes all previous access tokens
        """
        auth_method = config.get("credentials", {}).get("auth_method")
        if not auth_method or auth_method == "access_token":
            # support of backward compatibility with old exists configs
            access_token = config["credentials"]["access_token"] if auth_method else config["access_token"]
            return TokenAuthenticator(token=access_token)
        elif auth_method == "oAuth2.0":
            return LinkedinAdsOAuth2Authenticator(
                token_refresh_endpoint="https://www.linkedin.com/oauth/v2/accessToken",
                client_id=config["credentials"]["client_id"],
                client_secret=config["credentials"]["client_secret"],
                refresh_token=config["credentials"]["refresh_token"],
            )
        raise Exception("incorrect input parameters")

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        """
        Testing connection availability for the connector.
        :: for this check method the Customer must have the "r_liteprofile" scope enabled.
        :: more info: https://docs.microsoft.com/linkedin/consumer/integrations/self-serve/sign-in-with-linkedin
        """

        config["authenticator"] = self.get_authenticator(config)
        stream = Accounts(config)
        # need to load the first item only
        stream.records_limit = 1
        try:
            next(stream.read_records(sync_mode=SyncMode.full_refresh), None)
            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        Mapping a input config of the user input configuration as defined in the connector spec.
        Passing config to the streams.
        """
        config["authenticator"] = self.get_authenticator(config)
        return [
            Accounts(config),
            AccountUsers(config),
            AdCampaignAnalytics(config),
            AdCreativeAnalytics(config),
            AdDirectSponsoredContents(config),
            CampaignGroups(config),
            Campaigns(config),
            Creatives(config),
        ]
