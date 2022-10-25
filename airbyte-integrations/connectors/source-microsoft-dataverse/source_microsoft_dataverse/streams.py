#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import datetime
from abc import ABC

from typing import Any, Iterable, Mapping, MutableMapping, Optional

import requests
from airbyte_cdk.sources.streams import IncrementalMixin
from airbyte_cdk.sources.streams.http import HttpStream

from urllib import parse
import logging


# Basic full refresh stream
class MicrosoftDataverseStream(HttpStream, ABC):

    # Base url will be set by init(), using information provided by the user through config input
    url_base = ""

    def __init__(self, url, **kwargs):
        super().__init__(**kwargs)
        self.url_base = url + "/api/data/v9.2/"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        :param response: the most recent response from the API
        :return If there is another page in the result, a mapping (e.g: dict) containing information needed to query the next page in the response.
                If there are no more pages in the result, return None.
        """
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        for result in response.json()["value"]:
            yield result

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        """
        Override to return any non-auth headers. Authentication headers will overwrite any overlapping headers returned from this method.
        """
        return {"Cache-Control": "no-cache", "OData-Version": "4.0", "Content-Type": "application/json"}


# Basic incremental stream
class IncrementalMicrosoftDataverseStream(MicrosoftDataverseStream, IncrementalMixin, ABC):

    maxNumPages = 0
    numPagesRetrieved = 0
    odata_maxpagesize = 2000
    delta_token_field = "$deltatoken"
    today_date = None
    primary_key = ""

    def __init__(self, url, stream_name, schema, primary_key, max_num_pages, odata_maxpagesize, **kwargs):
        super().__init__(url, **kwargs)
        self.stream_name = stream_name
        self.primary_key = primary_key
        self.schema = schema
        self.maxNumPages = max_num_pages
        self.odata_maxpagesize = odata_maxpagesize
        self.today_date = datetime.datetime.combine(datetime.date.today(), datetime.time.max, datetime.timezone.utc)

    state_checkpoint_interval = None

    @property
    def name(self) -> str:
        """Source name"""
        return self.stream_name

    def get_json_schema(self) -> Mapping[str, Any]:
        return self.schema

    @property
    def supports_incremental(self):
        return True

    @property
    def update_field(self):
        return "modifiedon"

    @property
    def state(self) -> Mapping[str, Any]:
        return {self.delta_token_field: str(self._cursor_value)}

    @property
    def cursor_field(self) -> str:
        return "_ab_cdc_updated_at"    # Parameter returned inside response's deltaLink field

    # Sets the state got by state getter. "value" is the return of state getter -> dict
    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._cursor_value = value[self.delta_token_field]

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        """
        Override to return any non-auth headers. Authentication headers will overwrite any overlapping headers returned from this method.
        """
        dHeaders = super().request_headers(stream_state=stream_state)
        dHeaders.update({"Prefer": "odata.track-changes,odata.maxpagesize="+str(self.odata_maxpagesize)})  # odata.track-changes -> Header that enables change tracking
        return dHeaders

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        :return a dict containing the parameters to be used in the request
        """
        dParams = super().request_params(stream_state)
        # If there is not a nextLink(contains "next_page_token") in the response, means it is the last page.
        # In this case, the deltatoken is passed instead.
        if next_page_token is None:
            dParams.update(stream_state)
            return dParams
        elif next_page_token is not None:
            dParams.update(next_page_token)
            return dParams

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        responseJson = response.json()
        if "@odata.deltaLink" in responseJson:
            deltaLink = responseJson["@odata.deltaLink"]
            deltaLinkParams = dict(parse.parse_qsl(parse.urlsplit(deltaLink).query))
            self._cursor_value = deltaLinkParams[self.delta_token_field]
        for result in responseJson["value"]:
            if "@odata.context" in result and result["reason"] == "deleted":
                result.update({self.primary_key: result["id"]})
                result.pop("@odata.context", None)
                result.pop("id", None)
                result.pop("reason", None)
                result.update({"_ab_cdc_deleted_at": self.today_date.isoformat()})
            else:
                result.update({"_ab_cdc_updated_at": result[self.update_field]})

            yield result

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        :param response: the most recent response from the API
        :return If there is another page in the result, a mapping (e.g: dict) containing information needed to query the next page in the response.
                If there are no more pages in the result, return None.
        """
        
        responseJson = response.json()
        
        # $skiptoken is one of the parameters of nextLink alongside 
        # the other parameters(query, etc..) sent in the first request.  
        # It is used to get the next page. 
        if self.maxNumPages != 0 and self.numPagesRetrieved >= self.maxNumPages-1:
            logging.info(f"\nO limite de {self.maxNumPages} páginas foi atingido.\n")
            return None
        elif "@odata.nextLink" in responseJson:
            nextLink = responseJson["@odata.nextLink"]
            nextLinkParams = dict(parse.parse_qsl(parse.urlsplit(nextLink).query))
            self.numPagesRetrieved += 1
            return nextLinkParams
        else:
            return None

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return self.name + "s"
