#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_cdk.sources.streams.http.auth import NoAuth
import logging
import datetime

# Basic full refresh stream
class OutbrainAmplifyApiStream(HttpStream, ABC):

    url_base = "https://api.outbrain.com/amplify/v0.1/"

    def __init__(self,  marketer_id, ob_token_v1, authenticator, **kwargs):
        super().__init__(authenticator, **kwargs)
        self.marketer_id = marketer_id
        self.token = ob_token_v1
        self.start_date = str((datetime.date.today() - datetime.timedelta(days=8)).strftime("%Y-%m-%d"))


    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        header = {"OB-TOKEN-V1": self.token}
        return header



class Budgets(OutbrainAmplifyApiStream):

    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:

        marketer_id = self.marketer_id
        return f"marketers/{marketer_id}/budgets?detachedOnly=false"
    
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        return response.json().get("budgets")

class Campaigns(OutbrainAmplifyApiStream):
    primary_key = "id"
    request_pagination_limit = 50
    pagintation_token = 0

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        marketer_id = self.marketer_id
        return f"marketers/{marketer_id }/campaigns"
    
    
    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        count = int(response.json()['count'])
        Campaigns.pagintation_token = Campaigns.pagintation_token + count
        next_page_token =  Campaigns.pagintation_token

        if count  == Campaigns.request_pagination_limit :
            return  next_page_token
        else:
            return None
    
    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {"offset": next_page_token, "limit": Campaigns.request_pagination_limit}
    
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        return response.json().get("campaigns")
    
class PublisherSectionByCampaignPerformance(OutbrainAmplifyApiStream):

    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        marketer_id = self.marketer_id
        return f"reports/marketers/{marketer_id}/campaigns/sections"
    
    
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        return response.json().get("campaignResults")
    
    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        start_date = self.start_date
        end_date = str((datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d"))
        params = {"from": start_date, "to": end_date}
        return params
    

class PerformanceByCountry(OutbrainAmplifyApiStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        marketer_id = self.marketer_id
        return f"reports/marketers/{marketer_id}/geo?breakdown=country"
    
    
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        return response.json().get("results")
    
    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:

        start_date = self.start_date
        end_date = str((datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d"))
        params = {"from": start_date, "to": end_date}
        return params


# Basic incremental stream
class IncrementalOutbrainAmplifyApiStream(OutbrainAmplifyApiStream, ABC):
    def _chunk_date_range(self, start_date: datetime.date) -> List[Mapping[str, any]]:
        dates = []
        while start_date < datetime.date.today():
            dates.append({'date': start_date.strftime("%Y-%m-%d")})
            start_date += datetime.timedelta(days=1)
        return dates

    def stream_slices(self, sync_mode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None) -> Iterable[
        Optional[Mapping[str, any]]]:
        start_date = (datetime.date.today() - datetime.timedelta(days=8))
        return self._chunk_date_range(start_date)

    def request_params(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, **kwargs)
        if stream_slice:
            params["from"] = stream_slice.get("date")
            params["to"] = stream_slice.get("date")

        self.logger.info(f"PARAMS: start_date: {params['from']} end_date: {params['to']}")
        return params

class PerformanceByCountry(IncrementalOutbrainAmplifyApiStream):
    primary_key = ["id","date"]

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        marketer_id = self.marketer_id
        return f"reports/marketers/{marketer_id}/geo?breakdown=country"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        results = response.json().get("results", [])

        self.logger.info(f"SLICE: start_date: {stream_slice.get('date')}")

        for result in results:
            result["date"] = stream_slice.get("date")

        return results

class PublisherSectionByCampaignPerformance(IncrementalOutbrainAmplifyApiStream):
    primary_key = ["id","date"]

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        marketer_id = self.marketer_id
        return 'reports/marketers/' + marketer_id + '/campaigns/sections'

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        results = response.json().get("campaignResults", [])

        self.logger.info(f"SLICE: start_date: {stream_slice.get('date')}")

        for result in results:
            result["date"] = stream_slice.get("date")

        return results

# Source
class SourceOutbrainAmplifyApi(AbstractSource):
    url = 'https://api.outbrain.com/amplify/v0.1/login'

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        auth=requests.auth.HTTPBasicAuth(config["USERNAME"], config["PASSWORD"])
        check_connection_respone = (requests.get(self.url, auth=auth))

        if check_connection_respone.ok ==  True:
            return True, None
        else:
            return False,  "Unable to connect to Outbrain API with the provided credentials"
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth=requests.auth.HTTPBasicAuth(config["USERNAME"], config["PASSWORD"])
        response = (requests.get(self.url, auth=auth))
        token = response.json()['OB-TOKEN-V1']
        authenticator = NoAuth()

        return [
            Budgets(marketer_id= config['MARKETER_ID'], ob_token_v1=token, authenticator=authenticator), 
            Campaigns(marketer_id= config['MARKETER_ID'], ob_token_v1=token, authenticator=authenticator),
            PublisherSectionByCampaignPerformance(marketer_id= config['MARKETER_ID'], ob_token_v1=token, authenticator=authenticator),
            PerformanceByCountry(marketer_id= config['MARKETER_ID'], ob_token_v1=token, authenticator=authenticator)
        ]
