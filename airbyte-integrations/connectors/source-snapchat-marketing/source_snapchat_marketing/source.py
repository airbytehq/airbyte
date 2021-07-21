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
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib.parse import parse_qsl, urlparse

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import Oauth2Authenticator

"""
TODO: Most comments in this class are instructive and should be deleted after the source is implemented.

This file provides a stubbed example of how to use the Airbyte CDK to develop both a source connector which supports full refresh or and an
incremental syncs from an HTTP API.

The various TODOs are both implementation hints and steps - fulfilling all the TODOs should be sufficient to implement one basic and one incremental
stream from a source. This pattern is the same one used by Airbyte internally to implement connectors.

The approach here is not authoritative, and devs are free to use their own judgement.

There are additional required TODOs in the files within the integration_tests folder and the spec.json file.
"""


class SnapchatMarketingException(Exception):
    """ Just for formatting the exception as SnapchatMarketing"""


# Basic full refresh stream
class SnapchatMarketingStream(HttpStream, ABC):
    data_field = None
    url_base = "https://adsapi.snapchat.com/v1/"
    primary_key = "id"
    items_per_page_limit = 1000

    def __init__(self, start_date, **kwargs):
        super().__init__(**kwargs)
        self.start_date = pendulum.parse(start_date).to_rfc3339_string()

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        next_page_cursor = response.json().get("paging", False)
        if next_page_cursor:
            return {"cursor": dict(parse_qsl(urlparse(next_page_cursor["next_link"]).query))["cursor"]}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params_payload = {}
        if next_page_token:
            params_payload.update(next_page_token)

        if self.items_per_page_limit:
            params_payload["limit"] = self.items_per_page_limit

        return params_payload

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        if isinstance(self.data_field, list) and len(self.data_field) == 2:
            json_response = response.json().get(self.data_field[0])
            for resp in json_response:
                yield resp.get(self.data_field[1])
        else:
            error_text = f"Cannot parse response. Data field unrecognized: {self.data_field}"
            self.logger.error(error_text)
            raise SnapchatMarketingException(error_text)


class IncrementalSnapchatMarketingStream(SnapchatMarketingStream, ABC):
    state_checkpoint_interval = SnapchatMarketingStream.items_per_page_limit
    cursor_field = "updated_at"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        if current_stream_state is not None and self.cursor_field in current_stream_state:
            return {self.cursor_field: max(current_stream_state[self.cursor_field], latest_record[self.cursor_field])}
        else:
            return {self.cursor_field: self.start_date}

    def read_records(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        records = super().read_records(**kwargs)
        if stream_state:
            for record in records:
                if record[self.cursor_field] >= stream_state.get(self.cursor_field):
                    yield record
        else:
            yield from records


class Organizations(SnapchatMarketingStream):
    """ Docs: https://marketingapi.snapchat.com/docs/#organizations """

    data_field = ["organizations", "organization"]

    def path(self, **kwargs) -> str:
        return "me/organizations"


class AdAccounts(IncrementalSnapchatMarketingStream):
    """ Docs: https://marketingapi.snapchat.com/docs/#get-all-ad-accounts """

    data_field = ["adaccounts", "adaccount"]

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        organizations_stream = Organizations(authenticator=self.authenticator, start_date=self.start_date)
        organizations_records = organizations_stream.read_records(sync_mode=SyncMode.full_refresh)
        organization_ids = [organization["id"] for organization in organizations_records]

        if not organization_ids:
            self.logger.error(
                "No organizations found. Ad Accounts cannot be extracted without organizations. "
                "Check https://marketingapi.snapchat.com/docs/#get-all-ad-accounts"
            )
            yield from []

        for organization_id in organization_ids:
            yield {"organization_id": organization_id}

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return "organizations/{}/adaccounts".format(stream_slice["organization_id"])


class Creatives(IncrementalSnapchatMarketingStream):
    """ Docs: https://marketingapi.snapchat.com/docs/#get-all-creatives """

    data_field = ["creatives", "creative"]

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        # The trick with this code is that all 3 streams are chained:
        # Organizations -> AdAccounts -> Creatives.
        # AdAccounts need the organization_id as path variable
        # Creatives need the ad_account_id as path variable
        # So first we must get the AdAccounts, then do the slicing for them
        # and then call the read_records for each slice

        ad_accounts_stream = AdAccounts(authenticator=self.authenticator, start_date=self.start_date)
        ad_accounts_slices = ad_accounts_stream.stream_slices(**kwargs)
        ad_account_ids = []
        for ad_accounts_slice in ad_accounts_slices:
            ad_accounts_records = ad_accounts_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=ad_accounts_slice)
            ad_account_ids += [ad_account["id"] for ad_account in ad_accounts_records]

        if not ad_account_ids:
            self.logger.error(
                "No ad_accounts found. Creatives cannot be extracted without organizations. "
                "Check https://marketingapi.snapchat.com/docs/#get-all-creatives"
            )
            yield from []

        for ad_account_id in ad_account_ids:
            yield {"ad_account_id": ad_account_id}

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return "adaccounts/{}/creatives".format(stream_slice["ad_account_id"])


class SnapchatAdsOauth2Authenticator(Oauth2Authenticator):
    """Request example for API token extraction:
    curl -X POST https://accounts.snapchat.com/login/oauth2/access_token \
      -d "refresh_token={refresh_token}" \
      -d "client_id={client_id}" \
      -d "client_secret={client_secret}"  \
      -d "grant_type=refresh_token"  \
    """

    def __init__(self, config):
        super().__init__(
            token_refresh_endpoint="https://accounts.snapchat.com/login/oauth2/access_token",
            client_id=config["client_id"],
            client_secret=config["secret"],
            refresh_token=config["refresh_token"],
        )

    # def refresh_access_token(self) -> Tuple[str, int]:
    #     """
    #     returns a tuple of (access_token, token_lifespan_in_seconds)
    #     """
    #     response_json = None
    #     try:
    #         response = requests.request(method="POST", url=self.token_refresh_endpoint, data=self.get_refresh_request_body())
    #         response_json = response.json()
    #         response.raise_for_status()
    #         return response_json["access_token"], response_json["expires_in"]
    #     except requests.exceptions.RequestException as e:
    #         # if response_json and "error" in response_json:
    #         #     raise Exception(
    #         #         "Error refreshing access token. Error: {}; Error details: {}; Exception: {}".format(
    #         #             response_json["error"], response_json["error_description"], e
    #         #         )
    #         #     ) from e
    #         raise Exception(f"Error refreshing access token: {e}") from e


# Source
class SourceSnapchatMarketing(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:

        try:
            auth = SnapchatAdsOauth2Authenticator(config)

            token = auth.get_access_token()

            url = "https://adsapi.snapchat.com/v1/me"

            session = requests.get(url, headers={"Authorization": "Bearer {}".format(token)})
            session.raise_for_status()
            return True, None

        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = SnapchatAdsOauth2Authenticator(config)
        kwargs = {"authenticator": auth, "start_date": config["start_date"]}
        return [Organizations(**kwargs), AdAccounts(**kwargs), Creatives(**kwargs)]
