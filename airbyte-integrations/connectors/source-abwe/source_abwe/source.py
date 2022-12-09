#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

import requests
import json
from datetime import datetime, timedelta, date
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream, IncrementalMixin
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator, HttpAuthenticator

# Basic full refresh stream
class AbweStream(HttpStream, ABC):

    primary_key = "TransactionDetailId"
    current_page = 1
    pull_amount = 1000
    url_base = "https://rock.abwe.org"

    def __init__(self, config: Mapping[str, Any], start_date: datetime, **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        current_page = self.current_page
        self.current_page = self.current_page + 1

        end_date = self.start_date + timedelta(days=1)

        #If it return less than 1000 and we aren't up to today, go to the next date
        if (response.text.strip() == "" or len(response.json()) < self.pull_amount) and datetime.today() > end_date:
            self.current_page = 1
            self.start_date = end_date
        elif datetime.today() <= end_date:
            return None

        return {'Page': self.current_page, 'StartDate': self.start_date, 'EndDate': self.start_date }
        
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        if response.text.strip() != "":
            yield from response.json()
        else:
            yield from []

# Basic incremental stream
class IncrementalAbweStream(AbweStream, IncrementalMixin):

    state_checkpoint_interval = 100
    primary_key = "TransactionDetailId"

    def __init__(self, config: Mapping[str, Any], start_date: datetime, **kwargs):
        super().__init__(config, start_date, **kwargs)
        self._cursor_value = start_date

    @property
    @abstractmethod
    def cursor_field(self) -> str:
        """
        Defining a cursor field indicates that a stream is incremental, so any incremental stream must extend this class
        and define a cursor field.
        """
        pass


class Gifts(IncrementalAbweStream):

    cursor_field = "TransactionDateTime"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        if self.current_page > 1:
            return "/Webhooks/Lava.ashx/Donations_NextAfter?StartDate=" + self.start_date.strftime("%Y-%m-%d") + "&EndDate=" + self.start_date.strftime("%Y-%m-%d") + "&Page=" + str(self.current_page)
        
        return "/Webhooks/Lava.ashx/Donations_NextAfter?StartDate=" + self.start_date.strftime("%Y-%m-%d") + "&EndDate=" + self.start_date.strftime("%Y-%m-%d")

    @property
    def state(self) -> Mapping[str, Any]:
        return {self.cursor_field: self.start_date}
    
    @state.setter
    def state(self, value: Mapping[str, Any]):
        if self.cursor_field in value and value[self.cursor_field]:
            #To ensure the date is less than the most recent record, just reduce by one day
            self._cursor_value = datetime.strptime(value[self.cursor_field], "%Y-%m-%dT%H:%M:%S") - timedelta(days=1)
            self.start_date = datetime.strptime(value[self.cursor_field], "%Y-%m-%dT%H:%M:%S") - timedelta(days=1)


class AbweAuthenticator(HttpAuthenticator):

    def __init__(self, token: str):
        self.auth_token = token

    def get_auth_header(self) -> Mapping[str, Any]:
        return {"Authorization-Token": f"{self.auth_token}"}

# Source
class SourceAbwe(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:

        auth_token = config["auth_token"]
        if len(auth_token) != 24:
            return False, f"The Auth Token entered is not valid. It must be 24 characters long."
        else:
            return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:

        auth = AbweAuthenticator(token=config["auth_token"])
        start_date = datetime.strptime(config["start_date"], "%Y-%m-%d"),

        return [
            Gifts(authenticator=auth, config=config, start_date=start_date[0]) 
        ]
