#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

import requests
import json
from datetime import datetime, timedelta
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream, IncrementalMixin
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


# Basic full refresh stream
class VirtuousCrmStream(HttpStream, ABC):

    primary_key = "id"
    current_step = 0
    pull_amount = 1000

    url_base = "https://api.virtuoussoftware.com/api/"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        self.current_step = self.current_step + self.pull_amount
        if response.json()["total"] < self.current_step:
            self.current_step = 0 #reset it for Communications
            return None
        else:
            return {'skip': self.current_step }
        
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        yield from response_json.get("list", [])

    @property
    def http_method(self) -> str:
        return "POST"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        if next_page_token:
            return { "skip":  str(next_page_token['skip']), "take": str(self.pull_amount) }
        else:
            return { "skip": "0", "take": str(self.pull_amount)}

    def request_body_json(self, **kwargs) -> Optional[Mapping]:
        return { 
            "sortBy": "Id",
            "descending": False
        }

class ChildStreamMixin:
    parent_stream_class: Optional[VirtuousCrmStream] = None

    def stream_slices(self, sync_mode, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        for item in self.parent_stream_class(authenticator=self.authenticator).read_records(sync_mode=sync_mode):
            yield {"campaignId": item["campaignId"]}

class Contacts(VirtuousCrmStream):

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "Contact/Query/FullContact"


class Gifts(VirtuousCrmStream):
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "Gift/Query/FullGift"


class Campaigns(VirtuousCrmStream):

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "Campaign/Query"

    def request_body_json(self, **kwargs) -> Optional[Mapping]:
        return { 
            "sortBy": "campaignId",
            "descending": False
        }


class Segments(VirtuousCrmStream):
    pull_amount = 100000 #paging doesn't work with Segments so just get A LOT OF THEM

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "Segment/Search"

    def request_body_json(self, **kwargs) -> Optional[Mapping]:
        return { 
            "search": ""
        }

class Communications(ChildStreamMixin, VirtuousCrmStream):

    parent_stream_class = Campaigns
    pull_amount = 100 #There is a different max take of 100 for Communications

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"Communication/ByCampaign/{stream_slice['campaignId']}"

    def request_body_json(self, **kwargs) -> Optional[Mapping]:
        return {}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        if next_page_token:
            return { "skip":  str(next_page_token['skip']), "take": str(self.pull_amount), 
                "sortBy": "CreatedDateTime", "descending" : False}
        else:
            return { "skip": "0", "take": str(self.pull_amount), 
                "sortBy": "CreatedDateTime", "descending" : False}

    @property
    def http_method(self) -> str:
        return "GET"


# Basic incremental stream
class IncrementalVirtuousCrmStream(VirtuousCrmStream, IncrementalMixin):

    state_checkpoint_interval = 100
    primary_key = "id"

    def __init__(self, config: Mapping[str, Any], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cursor_value = None

    @property
    @abstractmethod
    def cursor_field(self) -> str:
        """
        Defining a cursor field indicates that a stream is incremental, so any incremental stream must extend this class
        and define a cursor field.
        """
        pass

class Gifts(IncrementalVirtuousCrmStream):

    cursor_field = "giftDate"
    start_date = ""

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "Gift/Query/FullGift"

    def request_body_json(self, **kwargs) -> Optional[Mapping]:
        if self.start_date != "":
            return { 
                "sortBy": self.cursor_field,
                "descending": False,
                "groups" : [{
                    "conditions": [{
                        "parameter": "Gift Date",
                        "operator": "GreaterThanOrEqual",
                        "value": self.start_date
                    }]
                }]
            }
        else:
            return { 
                "sortBy": self.cursor_field,
                "descending": False
            }
    def read_records(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        for record in super().read_records(*args, **kwargs):
            gift_date = record[self.cursor_field]
            if self._cursor_value:
                self._cursor_value = max(self._cursor_value, gift_date)
            else:
                self._cursor_value = gift_date
            yield record

    @property
    def state(self) -> Mapping[str, Any]:
        return {self.cursor_field: self._cursor_value}
    
    @state.setter
    def state(self, value: Mapping[str, Any]):
        if self.cursor_field in value and value[self.cursor_field]:
            #To ensure the date is less than the most recent record, just reduce by one day
            cursor_date_time = datetime.strptime(value[self.cursor_field], "%Y-%m-%dT%H:%M:%S") - timedelta(days=60)
            self._cursor_value = cursor_date_time.strftime("%Y-%m-%dT%H:%M:%S")
            self.start_date = self._cursor_value


# Source
class SourceVirtuousCrm(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:

        api_key = config['api_key']
        if not api_key.startswith("v_", 0, 2) or len(api_key) != 350:
            return False, f"The API key entered is not valid. They must start with a 'v_' and be 350 characters long."
        else:
            return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:

        auth = TokenAuthenticator(token=config["api_key"], auth_method="Bearer")

        return [
            Gifts(authenticator=auth, config=config) 
            ,Contacts(authenticator=auth)
            ,Campaigns(authenticator=auth)
            ,Communications(authenticator=auth)
            ,Segments(authenticator=auth)
        ]
