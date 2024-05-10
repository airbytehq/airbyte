#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, Mapping, MutableMapping, Optional
from urllib.parse import quote, urlencode

import pendulum
import requests
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer

from .utils import get_parent_stream_values, transform_data

logger = logging.getLogger("airbyte")

LINKEDIN_VERSION_API = "202404"


class LinkedinAdsStream(HttpStream, ABC):
    """
    Basic class provides base functionality for all streams.
    """

    url_base = "https://api.linkedin.com/rest/"
    primary_key = "id"
    records_limit = 500
    transformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)

    def __init__(self, config: Dict):
        super().__init__(authenticator=config.get("authenticator"))
        self.config = config
        self.date_time_fields = self._get_date_time_items_from_schema()

    def _get_date_time_items_from_schema(self):
        """
        Get all properties from schema with format: 'date-time'
        """
        schema = self.get_json_schema()
        return [k for k, v in schema["properties"].items() if v.get("format") == "date-time"]

    @property
    def accounts(self):
        """Property to return the list of the user Account Ids from input"""
        return ",".join(map(str, self.config.get("account_ids", [])))

    @property
    @abstractmethod
    def endpoint(self) -> str:
        """Endpoint associated with the current stream"""

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
        Cursor based pagination using the pageSize and pageToken parameters.
        """
        parsed_response = response.json()
        if parsed_response.get("metadata", {}).get("nextPageToken"):
            return {"pageToken": parsed_response["metadata"]["nextPageToken"]}
        else:
            return None

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
        params = {"pageSize": self.records_limit, "q": "search"}
        if next_page_token:
            params.update(**next_page_token)
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        We need to get out the nested complex data structures for further normalization, so the transform_data method is applied.
        """
        for record in transform_data(response.json().get("elements")):
            yield self._date_time_to_rfc3339(record)

    def _date_time_to_rfc3339(self, record: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        """
        Transform 'date-time' items to RFC3339 format
        """
        for item in record:
            if item in self.date_time_fields and record[item]:
                record[item] = pendulum.parse(record[item]).to_rfc3339_string()
        return record

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


class OffsetPaginationMixin:
    """Mixin for offset based pagination for endpoints tha tdoesnt support cursor based pagination"""

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

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        To paginate through results, begin with a start value of 0 and a count value of N.
        To get the next page, set start value to N, while the count value stays the same.
        We have reached the end of the dataset when the response contains fewer elements than the `count` parameter request.
        https://docs.microsoft.com/en-us/linkedin/shared/api-guide/concepts/pagination?context=linkedin/marketing/context
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
        return {"start": paging_params.get("start") + self.records_limit}


class Accounts(LinkedinAdsStream):
    """
    Get Accounts data. More info about LinkedIn Ads / Accounts:
    https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-accounts?tabs=http&view=li-lms-2023-05#search-for-accounts
    """

    endpoint = "adAccounts"
    use_cache = True

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
        so the urlencode(..., safe=":(),%") is used instead, to keep the values as they are.
        """
        params = super().request_params(stream_state, stream_slice, next_page_token)
        if self.accounts:
            # Construct the URN for each account ID
            accounts = [f"urn:li:sponsoredAccount:{account_id}" for account_id in self.config.get("account_ids")]

            # Join the URNs into a single string, separated by commas, and URL encode only this part
            encoded_accounts = quote(",".join(accounts), safe=",")

            # Insert the encoded account IDs into the overall structure, keeping colons and parentheses outside safe
            params["search"] = f"(id:(values:List({encoded_accounts})))"
        return urlencode(params, safe=":(),%")


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
    def parent_stream(self) -> LinkedinAdsStream:
        """Defines the parent stream for slicing, the class object should be provided."""

    @property
    def state_checkpoint_interval(self) -> Optional[int]:
        """Define the checkpoint from the record output size."""
        return 100

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        current_stream_state = {self.cursor_field: self.config.get("start_date")} if not current_stream_state else current_stream_state
        return {self.cursor_field: max(latest_record.get(self.cursor_field), current_stream_state.get(self.cursor_field))}


class LinkedInAdsStreamSlicing(IncrementalLinkedinAdsStream, ABC):
    """
    This class stands for provide stream slicing for other dependent streams.
    :: `parent_stream` - the reference to the parent stream class,
        by default it's referenced to the Accounts stream class, as far as a majority of streams are using it.
    :: `parent_values_map` - key_value map for stream slices in a format: {<slice_key_name>: <key inside record>}
    :: `search_param` - the query param to pass with request_params
    """

    parent_stream = Accounts
    parent_values_map = {"account_id": "id"}

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


class AccountUsers(OffsetPaginationMixin, LinkedInAdsStreamSlicing):
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
    use_cache = True

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
    # standard records_limit=500 returns error 400: Request would return too many entities; https://github.com/airbytehq/oncall/issues/2159
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


class Conversions(OffsetPaginationMixin, LinkedInAdsStreamSlicing):
    """
    Get Conversions data using `account_id` slicing.
    https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads-reporting/conversion-tracking?view=li-lms-2023-05&tabs=curl#find-conversions-by-ad-account
    """

    endpoint = "conversions"
    search_param = "account"

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        headers = super().request_headers(stream_state, stream_slice, next_page_token)
        headers.update({"X-Restli-Protocol-Version": "2.0.0"})
        return headers

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        params["q"] = self.search_param
        params["account"] = f"urn%3Ali%3AsponsoredAccount%3A{stream_slice.get('account_id')}"

        return urlencode(params, safe="():,%")

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        current_stream_state = (
            {self.cursor_field: pendulum.parse(self.config.get("start_date")).format("x")}
            if not current_stream_state
            else current_stream_state
        )
        return {self.cursor_field: max(latest_record.get(self.cursor_field), int(current_stream_state.get(self.cursor_field)))}
