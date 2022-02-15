#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from re import A
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from datetime import date, timedelta

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator

class TaboolaCampaignSummaryStream(HttpStream, ABC):
    url_base = "https://backstage.taboola.com/backstage/api/1.0/"

    def __init__(self, account_id: str, **kwargs):
        super().__init__(**kwargs)
        self.account_id = account_id

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json().get("results", [])


class Campaigns(TaboolaCampaignSummaryStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"{self.account_id}/campaigns"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

class DailyPerCampaignSite(TaboolaCampaignSummaryStream):
    primary_key = ["date", "site", "campaign"]

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"{self.account_id}/reports/campaign-summary/dimensions/campaign_site_day_breakdown"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        start_date = (date.today() - timedelta(days=7)).strftime("%Y-%m-%d")
        end_date = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
        return {
            "start_date": start_date,
            "end_date": end_date
        }

class IncrementalTaboolaCampaignSummaryStream(TaboolaCampaignSummaryStream, ABC):
    cursor_field = "date"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        return {
            "date": date.today().strftime("%Y-%m-%d")
        }

    def _chunk_date_range(self, start_date: date) -> List[Mapping[str, any]]:
        dates = []
        while start_date < date.today():
            dates.append({'date': start_date.strftime("%Y-%m-%d")})
            start_date += timedelta(days=1)
        return dates

    def stream_slices(self, sync_mode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None) -> Iterable[
        Optional[Mapping[str, any]]]:
        start_date = (date.today() - timedelta(days=7))
        return self._chunk_date_range(start_date)

    def request_params(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, **kwargs)
        if stream_slice:
            params["start_date"] = stream_slice.get("date")
            params["end_date"] = stream_slice.get("date")

        self.logger.info(f"PARAMS: start_date: {params['start_date']} end_date: {params['end_date']}")
        return params

class DailyPerCountry(IncrementalTaboolaCampaignSummaryStream):
    primary_key = ["date", "country"]

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"{self.account_id}/reports/campaign-summary/dimensions/country_breakdown"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        results = response.json().get("results", [])

        for result in results:
            result["date"] = stream_slice.get("date")

        return results

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

        response = requests.post(url, data=params)
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
            Campaigns(account_id=config["account_id"], authenticator=auth),
            DailyPerCampaignSite(account_id=config["account_id"], authenticator=auth),
            DailyPerCountry(account_id=config["account_id"], authenticator=auth)
        ]
