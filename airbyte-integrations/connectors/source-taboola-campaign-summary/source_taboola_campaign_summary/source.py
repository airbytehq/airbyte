#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from re import A
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

class TaboolaCampaignSummaryStream(HttpStream, ABC):
    url_base = "https://backstage.taboola.com/backstage/api/1.0/"

    def __init__(self, account_id: str, initial_date: str, **kwargs):
        super().__init__(**kwargs)
        self.account_id = account_id
        self.initial_date = initial_date

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json().get("results", [])


class Campaigns(TaboolaCampaignSummaryStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"{self.account_id}/campaigns"


class IncrementalTaboolaCampaignSummaryStream(TaboolaCampaignSummaryStream, ABC):
    state_checkpoint_interval = None

    @property
    def cursor_field(self) -> str:
        pass

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        return {self.cursor_field: max(latest_record.get(self.cursor_field, 0), current_stream_state.get(self.cursor_field, 0))}

    def request_params(self, stream_state=None, **kwargs):
        stream_state = stream_state or {}
        params = super().request_params(stream_state=stream_state, **kwargs)
        if stream_state:
            params["start_date"] = stream_state.get(self.cursor_field)
        return params


class DailyPerCampaignSite(IncrementalTaboolaCampaignSummaryStream):

    cursor_field = "date"
    primary_key = ["date", "campaign", "site"]

    def path(self, **kwargs) -> str:
        return f"{self.account_id}/reports/campaign-summary/dimensions/campaign_site_day_breakdown"


class SourceTaboolaCampaignSummary(AbstractSource):
    def get_authenticator(self, client_id, client_secret) -> TokenAuthenticator:
        token = self.get_access_token(client_id=client_id, client_secret=client_secret)
        return TokenAuthenticator(token=token)

    def get_access_token(self, client_id, client_secret) -> str:
        url = "https://backstage.taboola.com/backstage/oauth/token"
        params = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials"
        }

        response = requests.post(url, params=params)
        response.raise_for_status()
        json_response = response.json()
        return json_response.get("access_token", None)

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        auth = self.get_authenticator(config["client_id"], config["client_secret"])
        url = f"{TaboolaCampaignSummaryStream.url_base}users/current/account"
        try:
            response = requests.get(url, headers=auth.get_auth_header())
            response.raise_for_status()
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = self.get_authenticator(config["client_id"], config["client_secret"])
        return [
            Campaigns(account_id=config["account_id"], initial_Date=config["initial_date"], authenticator=auth),
            DailyPerCampaignSite(account_id=config["account_id"], initial_Date=config["initial_date"], authenticator=auth)
        ]
