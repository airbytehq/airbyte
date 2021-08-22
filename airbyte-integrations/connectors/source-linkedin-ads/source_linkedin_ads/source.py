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

import requests
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


class LinkedinAdsStream(HttpStream, ABC):

    url_base = "https://api.linkedin.com/v2/"
    primary_key = "id"
    limit = 500

    def __init__(self, config: Dict):
        super().__init__(authenticator=config["authenticator"])
        self.config = config
        self.start_date = config["start_date"]

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        https://docs.microsoft.com/en-us/linkedin/shared/api-guide/concepts/pagination?context=linkedin/marketing/context
        """
        if len(response.json().get("elements")) < self.limit:
            return None
        return {"start": response.json().get("paging").get("start") + self.limit}
        
    def request_params(self, stream_state: Mapping[str, Any], next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        params = {"count": self.limit, "q": "search"}
        if next_page_token:
            params.update(**next_page_token)
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json().get("elements")


class LinkedinAdsStreamMixin(LinkedinAdsStream):

    search_param = "search.account.values[0]"
    search_value = "urn:li:sponsoredAccount:"

    def request_params(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, **kwargs)
        params[self.search_param] = f"{self.search_value}{stream_slice.get('account_id')}"
        return params

    def read_records(self, stream_state: Mapping[str, Any] = None, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        stream_state = stream_state or {}
        accounts_stream = Accounts(config=self.config)
        for data in accounts_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield from super().read_records(stream_slice={"account_id": data[self.primary_key]}, **kwargs)


class Accounts(LinkedinAdsStream):
    """
    Get Accounts data.
    More info about LinkedIn Ads / Accounts:
    https://docs.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-accounts?tabs=http
    """
    #TODO: add ability to use the account_ids from user's spec in UI
    #TODO: edit schema based on example response from link

    def path(self, **kwargs) -> str:
        return "adAccountsV2"

class AccountUsers(LinkedinAdsStreamMixin):
    """
    Get AccountUsers data using `account_id` slicing.
    More info about LinkedIn Ads / AccountUsers:
    https://docs.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-account-users?tabs=http
    """

    search_param = "accounts"

    def path(self, **kwargs) -> str:
        return "adAccountUsersV2"

    def request_params(self, stream_state: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, **kwargs)
        params["q"] = self.search_param
        return params


class CampaignGroups(LinkedinAdsStreamMixin):
    """
    Get CampaignGroups data using `account_id` slicing.
    More info about LinkedIn Ads / CampaignGroups:
    https://docs.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-campaign-groups?tabs=http
    """
    #TODO: edit schema based on example response from link

    def path(self, **kwargs) -> str:
        return "adCampaignGroupsV2"


class Campaigns(LinkedinAdsStreamMixin):
    """
    Get Campaigns data using `account_id` slicing.
    More info about LinkedIn Ads / Campaigns:
    https://docs.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-campaigns?tabs=http
    """
    #TODO: edit schema based on example response from link

    def path(self, **kwargs) -> str:
        return "adCampaignsV2"




class IncrementalLinkedinAdsStream(LinkedinAdsStream, ABC):

    @property
    def limit(self):
        return self.limit

    state_checkpoint_interval = limit

    @property
    def cursor_field(self) -> str:
        return []

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest record and
        the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
        """
        return {}


class Employees(IncrementalLinkedinAdsStream):

    cursor_field = "start_date"

    # TODO: Fill in the primary key. Required. This is usually a unique field in the stream, like an ID or a timestamp.
    primary_key = "employee_id"

    def path(self, **kwargs) -> str:

        return "employees"

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:

        raise NotImplementedError("Implement stream slices or delete this method!")


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
            print(response.headers)
            return True, None
        except requests.exceptions.HTTPError as e:
            return False, f"{e}, {response.json().get('message')}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        Mapping a input config of the user input configuration as defined in the connector spec.
        Passing config to the streams.
        """

        config["authenticator"] = TokenAuthenticator(token=config["access_token"])

        return [
            Accounts(config),
            AccountUsers(config),
            CampaignGroups(config),
            Campaigns(config)
        ]
