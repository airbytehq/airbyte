#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, Mapping, MutableMapping, Optional
from urllib.parse import urlencode

import pendulum
import requests
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer

from .analytics import make_analytics_slices, merge_chunks, update_analytics_params
from .utils import get_parent_stream_values, transform_data

logger = logging.getLogger("airbyte")

LINKEDIN_VERSION_API = "202305"


class LinkedinAdsStream(HttpStream, ABC):
    """
    Basic class provides base functionality for all streams.
    """

    url_base = "https://api.linkedin.com/rest/"
    primary_key = "id"
    records_limit = 500
    endpoint = None
    transformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)

    def __init__(self, config: Dict):
        super().__init__(authenticator=config.get("authenticator"))
        self.config = config

    @property
    def accounts(self):
        """Property to return the list of the user Account Ids from input"""
        return ",".join(map(str, self.config.get("account_ids")))

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
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

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {"Linkedin-Version": LINKEDIN_VERSION_API}

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
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
    https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-accounts?tabs=http&view=li-lms-2023-05#search-for-accounts
    """

    endpoint = "adAccounts"

    def request_headers(self, stream_state: Mapping[str, Any], **kwargs) -> Mapping[str, Any]:
        """
        If account_ids are specified as user's input from configuration,
        we must use MODIFIED header: {'X-RestLi-Protocol-Version': '2.0.0'}
        """
        headers = super().request_headers(stream_state, **kwargs)
        headers.update({"X-RestLi-Protocol-Version": "2.0.0"} if self.accounts else {})
        return headers

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        """
        Override request_params() to have the ability to accept the specific account_ids from user's configuration.
        If we have list of account_ids, we need to make sure that the request_params are encoded correctly,
        We will get HTTP Error 500, if we use standard requests.urlencode methods to parse parameters,
        so the urlencode(..., safe=":(),") is used instead, to keep the values as they are.
        """
        params = super().request_params(stream_state, stream_slice, next_page_token)
        if self.accounts:
            params["search"] = f"(id:(values:List({self.accounts})))"
        return urlencode(params, safe="():,%")


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

    @property
    @abstractmethod
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
    """

    parent_stream = Accounts
    parent_values_map = {"account_id": "id"}
    # define default additional request params

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
    https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-account-users?tabs=http&view=li-lms-2023-05#find-ad-account-users-by-accounts
    """

    endpoint = "adAccountUsers"
    # Account_users stream doesn't have `id` property, so the "account" is used instead.
    primary_key = "account"
    search_param = "accounts"

    def request_params(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, **kwargs)
        params["q"] = self.search_param
        params["accounts"] = f"urn:li:sponsoredAccount:{stream_slice.get('account_id')}"  # accounts=
        return urlencode(params, safe="():,%")


class CampaignGroups(LinkedInAdsStreamSlicing):
    """
    Get CampaignGroups data using `account_id` slicing.
    More info about LinkedIn Ads / CampaignGroups:
    https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-campaign-groups?tabs=http&view=li-lms-2023-05#search-for-campaign-groups
    """

    endpoint = "adCampaignGroups"

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return f"{self.parent_stream.endpoint}/{stream_slice.get('account_id')}/{self.endpoint}"

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
        params = super().request_params(stream_state, stream_slice, next_page_token)
        params["search"] = "(status:(values:List(ACTIVE,ARCHIVED,CANCELED,DRAFT,PAUSED,PENDING_DELETION,REMOVED)))"
        return urlencode(params, safe="():,%")


class Campaigns(LinkedInAdsStreamSlicing):
    """
    Get Campaigns data using `account_id` slicing.
    More info about LinkedIn Ads / Campaigns:
    https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-campaigns?tabs=http&view=li-lms-2023-05#search-for-campaigns
    """

    endpoint = "adCampaigns"

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return f"{self.parent_stream.endpoint}/{stream_slice.get('account_id')}/{self.endpoint}"

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
        params = super().request_params(stream_state, stream_slice, next_page_token)
        params["search"] = "(status:(values:List(ACTIVE,PAUSED,ARCHIVED,COMPLETED,CANCELED,DRAFT,PENDING_DELETION,REMOVED)))"
        #
        return urlencode(params, safe="():,%")


class Creatives(LinkedInAdsStreamSlicing):
    """
    Get Creatives data using `campaign_id` slicing.
    More info about LinkedIn Ads / Creatives:
    https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-creatives?tabs=http%2Chttp-update-a-creative&view=li-lms-2023-05#search-for-creatives
    """

    endpoint = "creatives"
    parent_stream = Accounts
    cursor_field = "lastModifiedAt"
    # standard records_limit=500 returns error 400: Request would return too many entities;  https://github.com/airbytehq/oncall/issues/2159
    records_limit = 100

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return f"{self.parent_stream.endpoint}/{stream_slice.get('account_id')}/{self.endpoint}"

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        headers = super().request_headers(stream_state, stream_slice, next_page_token)
        headers.update({"X-RestLi-Method": "FINDER"})
        return headers

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        params.update({"q": "criteria"})
        return urlencode(params, safe="():,%")

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        current_stream_state = (
            {self.cursor_field: pendulum.parse(self.config.get("start_date")).format("x")}
            if not current_stream_state
            else current_stream_state
        )
        return {self.cursor_field: max(latest_record.get(self.cursor_field), int(current_stream_state.get(self.cursor_field)))}


class LinkedInAdsAnalyticsStream(IncrementalLinkedinAdsStream, ABC):
    """
    AdAnalytics Streams more info:
    https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads-reporting/ads-reporting?tabs=curl&view=li-lms-2023-05#analytics-finder
    """

    endpoint = "adAnalytics"
    # For Analytics streams the primary_key is the entity of the pivot [Campaign URN, Creative URN, etc] + `end_date`
    primary_key = ["pivotValue", "end_date"]
    cursor_field = "end_date"

    @property
    def base_analytics_params(self) -> MutableMapping[str, Any]:
        """Define the base parameters for analytics streams"""
        return {"q": "analytics", "pivot": self.pivot_by, "timeGranularity": "(value:DAILY)"}

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
        params.update(**update_analytics_params(stream_slice))
        params[self.search_param] = f"List(urn%3Ali%3A{self.search_param_value}%3A{self.get_primary_key_from_slice(stream_slice)})"
        return urlencode(params, safe="():,%")

    def get_primary_key_from_slice(self, stream_slice) -> str:
        return stream_slice.get(self.primary_slice_key)

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

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        We need to get out the nested complex data structures for further normalisation, so the transform_data method is applied.
        """
        for rec in transform_data(response.json().get("elements")):
            yield rec | {"pivotValue": f"urn:li:{self.search_param_value}:{self.get_primary_key_from_slice(kwargs.get('stream_slice'))}"}


class AdCampaignAnalytics(LinkedInAdsAnalyticsStream):
    """
    Campaign Analytics stream.
    """

    endpoint = "adAnalytics"

    parent_stream = Campaigns
    parent_values_map = {"campaign_id": "id"}
    search_param = "campaigns"
    search_param_value = "sponsoredCampaign"
    pivot_by = "(value:CAMPAIGN)"


class AdCreativeAnalytics(LinkedInAdsAnalyticsStream):
    """
    Creative Analytics stream.
    """

    parent_stream = Creatives
    parent_values_map = {"creative_id": "id"}
    search_param = "creatives"
    search_param_value = "sponsoredCreative"
    pivot_by = "(value:CREATIVE)"

    def get_primary_key_from_slice(self, stream_slice) -> str:
        creative_id = stream_slice.get(self.primary_slice_key).split(":")[-1]
        return creative_id
