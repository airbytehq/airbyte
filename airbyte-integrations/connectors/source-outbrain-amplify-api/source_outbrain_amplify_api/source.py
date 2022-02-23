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

    def __init__(self,  marketer_id, ob_token_v1, authenticator, start_date, **kwargs):
        super().__init__(authenticator, **kwargs)
        self.marketer_id = marketer_id
        self.token = ob_token_v1
        self.start_date = start_date


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

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        TODO: Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        yield {}


class Budgets(OutbrainAmplifyApiStream):

    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:

        marketer_id = self.marketer_id
        return 'https://api.outbrain.com/amplify/v0.1/marketers/' +marketer_id + '/budgets?detachedOnly=false'
    
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:

        return response.json().get("budgets")

class Campaigns(OutbrainAmplifyApiStream):
    """
    TODO: Change class name to match the table/data source this stream corresponds to.
    """

    # TODO: Fill in the primary key. Required. This is usually a unique field in the stream, like an ID or a timestamp.
    primary_key = "id"
    pagintation_token = 0

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        TODO: Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        marketer_id = self.marketer_id
        return 'https://api.outbrain.com/amplify/v0.1/marketers/' +marketer_id + '/campaigns'
    
    
    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        count = int(response.json()['count'])
        Campaigns.pagintation_token = Campaigns.pagintation_token + count
        next_page_token =  Campaigns.pagintation_token
        # return next pagination token until count of records in call is != 25 (limit of records per call)
        if count  == 25 :
            return  next_page_token
        else:
            return None
    
    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        TODO: Override this method to define any query parameters to be set. Remove this method if you don't need to define request params.
        Usually contains common params e.g. pagination size etc.
        """
  
        return {"offset": next_page_token}
    
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        TODO: Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """

        return response.json().get("campaigns")
    
class PublisherSectionByCampaignPerformance(OutbrainAmplifyApiStream):
    """
    TODO: Change class name to match the table/data source this stream corresponds to.
    """
    
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        TODO: Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        marketer_id = self.marketer_id

        return 'https://api.outbrain.com/amplify/v0.1/reports/marketers/' +marketer_id + '/campaigns/sections'
    
    
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        TODO: Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """


        return response.json().get("campaignResults")
    
    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        TODO: Override this method to define any query parameters to be set. Remove this method if you don't need to define request params.
        Usually contains common params e.g. pagination size etc.
        """
        start_date = self.start_date
        end_date = str((datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d"))
        params = {"from": start_date, "to": end_date}
        return params
    

class PerformanceByCountry(OutbrainAmplifyApiStream):
    """
    TODO: Change class name to match the table/data source this stream corresponds to.
    """

    # TODO: Fill in the primary key. Required. This is usually a unique field in the stream, like an ID or a timestamp.
    
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        TODO: Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        marketer_id = self.marketer_id


        return 'https://api.outbrain.com/amplify/v0.1/reports/marketers/' +marketer_id + '/geo?breakdown=country'
    
    
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        TODO: Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """

        return response.json().get("results")
    
    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        TODO: Override this method to define any query parameters to be set. Remove this method if you don't need to define request params.
        Usually contains common params e.g. pagination size etc.
        """
        start_date = self.start_date
        end_date = str((datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d"))
        params = {"from": start_date, "to": end_date}
        return params


# Basic incremental stream
class IncrementalOutbrainAmplifyApiStream(OutbrainAmplifyApiStream, ABC):
    """
    TODO fill in details of this class to implement functionality related to incremental syncs for your connector.
         if you do not need to implement incremental sync for any streams, remove this class.
    """

    # TODO: Fill in to checkpoint stream reads after N records. This prevents re-reading of data if the stream fails for any reason.
    cursor_field_date = []

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest record and
        the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
        """
        return {
            "date": date.today().strftime("%Y-%m-%d")
        }
 
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
        return 'https://api.outbrain.com/amplify/v0.1/reports/marketers/' +marketer_id + '/geo?breakdown=country'

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
        return 'https://api.outbrain.com/amplify/v0.1/reports/marketers/' +marketer_id + '/campaigns/sections'

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

    @property
    def retry_factor(self) -> int:
         # For python backoff package expo backoff delays calculated according to formula:
        # delay = factor * base ** n where base is 2
        # With default factor equal to 5 and 5 retries delays would be 5, 10, 20, 40 and 80 seconds.
        # For exports stream there is a limit of 4 requests per minute.
        # With retry_factor == 1800, we avoid hitting the api rate limit of generating more than 2 token within 30mins
        return 1800

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        url = 'https://api.outbrain.com/amplify/v0.1/login'
    
        auth=requests.auth.HTTPBasicAuth(config["USERNAME"], config["PASSWORD"])
        check_connection_respone = (requests.get(url, auth=auth))

        if check_connection_respone.ok ==  True:
            return True, None
        else:
            return False,  "Unable to connect to Outbrain API with the provided credentials"


        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:

        url = 'https://api.outbrain.com/amplify/v0.1/login'
         
        auth=requests.auth.HTTPBasicAuth(config["USERNAME"], config["PASSWORD"])
        response = (requests.get(url, auth=auth))
        token = response.json()['OB-TOKEN-V1']
        
        authenticator = NoAuth()
        return [Budgets(marketer_id= config['MARKETER_ID'], ob_token_v1=token, authenticator=authenticator,  start_date= config['START_DATE']), 
        Campaigns(marketer_id= config['MARKETER_ID'], ob_token_v1=token, authenticator=authenticator,start_date=config['START_DATE']),
        PublisherSectionByCampaignPerformance(marketer_id= config['MARKETER_ID'], ob_token_v1=token, authenticator=authenticator, start_date=config['START_DATE']),
        PerformanceByCountry(marketer_id= config['MARKETER_ID'], ob_token_v1=token, authenticator=authenticator, start_date=config['START_DATE'])]
