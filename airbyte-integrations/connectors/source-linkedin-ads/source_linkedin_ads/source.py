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


from abc import ABC
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib.parse import urlencode

import pendulum
import requests
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from .utils import transform_date_fields


class LinkedinAdsStream(HttpStream, ABC):

    url_base = "https://api.linkedin.com/v2/"
    primary_key = "id"
    limit = 900

    def __init__(self, config: Dict):
        super().__init__(authenticator=config["authenticator"])
        self.config = config
        self.start_date = pendulum.parse(config.get("start_date")).timestamp() * 1000
        self.accounts = config.get("account_ids", None)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        https://docs.microsoft.com/en-us/linkedin/shared/api-guide/concepts/pagination?context=linkedin/marketing/context
        """
        if len(response.json().get("elements")) < self.limit:
            return None
        return {"start": response.json().get("paging").get("start") + self.limit}

    def request_params(
        self, stream_state: Mapping[str, Any], next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        params = {"count": self.limit, "q": "search"}
        if next_page_token:
            params.update(**next_page_token)
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        records = response.json().get("elements")
        yield from transform_date_fields(records)


class IncrementalLinkedinAdsStream(LinkedinAdsStream, ABC):

    cursor_field = "lastModified"

    @property
    def limit(self):
        return super().limit

    state_checkpoint_interval = limit

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest record and
        the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
        """
        current_stream_state = {self.cursor_field: self.start_date} if not current_stream_state else current_stream_state
        return {self.cursor_field: max(latest_record.get(self.cursor_field, None), current_stream_state.get(self.cursor_field, None))}

    # Parse the stream_slice with respect to stream_state for Incremental refresh
    def filter_records_newer_than_state(self, stream_state: Mapping[str, Any] = None, records_slice: Mapping[str, Any] = None) -> Iterable:
        # Getting records >= state
        if stream_state:
            for record in records_slice:
                if record[self.cursor_field] >= stream_state.get(self.cursor_field):
                    yield record
        else:
            yield from records_slice


class AccountStreamMixin(IncrementalLinkedinAdsStream):
    """
    This class stands for provide stream slicing.
    :: Streams: AccountUsers, CampaignGroups, Campaigns

    :: `slice_key` - the key for slices dict.
    :: `search_param` - the query param to pass with request_params
    :: `search_value` - the value for `search_param` to pass with request_params
    """

    search_param = "search.account.values[0]"
    search_value = "urn:li:sponsoredAccount:"
    slice_key = "account_id"

    def request_params(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, **kwargs)
        params[self.search_param] = f"{self.search_value}{stream_slice.get(self.slice_key)}"
        return params

    def read_records(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs
    ) -> Iterable[Mapping[str, Any]]:
        stream_state = stream_state or {}
        accounts_stream = Accounts(config=self.config)
        for data in accounts_stream.read_records(sync_mode=SyncMode.full_refresh):
            slice = super().read_records(stream_slice={self.slice_key: data["id"]}, **kwargs)
            yield from self.filter_records_newer_than_state(stream_state=stream_state, records_slice=slice)


class Accounts(LinkedinAdsStream):
    """
    Get Accounts data. More info about LinkedIn Ads / Accounts:
    https://docs.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-accounts?tabs=http
    """

    def path(self, **kwargs) -> str:
        return "adAccountsV2"

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
            account_list = ",".join(map(str, self.config.get("account_ids")))
            params["search"] = f"(id:(values:List({account_list})))"
            return urlencode(params, safe=":(),")
        return params


class AccountUsers(AccountStreamMixin):
    """
    Get AccountUsers data using `account_id` slicing. More info about LinkedIn Ads / AccountUsers:
    https://docs.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-account-users?tabs=http
    """
    primary_key = None
    search_param = "accounts"

    def path(self, **kwargs) -> str:
        return "adAccountUsersV2"

    def request_params(self, stream_state: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, **kwargs)
        params["q"] = self.search_param
        return params


class CampaignGroups(AccountStreamMixin):
    """
    Get CampaignGroups data using `account_id` slicing.
    More info about LinkedIn Ads / CampaignGroups:
    https://docs.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-campaign-groups?tabs=http
    """

    def path(self, **kwargs) -> str:
        return "adCampaignGroupsV2"


class Campaigns(AccountStreamMixin):
    """
    Get Campaigns data using `account_id` slicing.
    More info about LinkedIn Ads / Campaigns:
    https://docs.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-campaigns?tabs=http
    """

    def path(self, **kwargs) -> str:
        return "adCampaignsV2"


class SourceLinkedinAds(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        """
        Testing connection availability for the connector.
        :: for this check method the Customer must have the "r_liteprofile" scope enabled.
        :: more info: https://docs.microsoft.com/linkedin/consumer/integrations/self-serve/sign-in-with-linkedin
        """

        header = TokenAuthenticator(token=config["access_token"]).get_auth_header()
        profile_url = "https://api.linkedin.com/v2/me"

        try:
            response = requests.get(url=profile_url, headers=header)
            response.raise_for_status()
            return True, None
        except requests.exceptions.RequestException as e:
            return False, f"{e}, {response.json().get('message')}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        Mapping a input config of the user input configuration as defined in the connector spec.
        Passing config to the streams.
        """

        config["authenticator"] = TokenAuthenticator(token=config["access_token"])

        return [Accounts(config), AccountUsers(config), CampaignGroups(config), Campaigns(config)]
