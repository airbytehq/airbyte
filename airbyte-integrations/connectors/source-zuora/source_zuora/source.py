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


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import json as j
import time
from itertools import chain
from math import ceil
import requests
import pendulum
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
# from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import HttpAuthenticator


class ZuoraAuthenticator(HttpAuthenticator):

    """
    Zuora Authenticator, based on generateToken()
    """

    def __init__(self, client_id: str, client_secret: str, is_sandbox: bool = True):
        self.client_id = client_id
        self.client_secret = client_secret
        self.is_sandbox = is_sandbox

    # Define Endpoint from is_sandbox arg
    @property
    def endpoint(self) -> str:
        if self.is_sandbox == True:
            return "https://rest.apisandbox.zuora.com"
        else: 
            return "https://rest.zuora.com"

    def generateToken(self):
        endpoint = f"{self.endpoint}/oauth/token"
        header = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {"client_id": f"{self.client_id}", 
                "client_secret" : f"{self.client_secret}",
                "grant_type": "client_credentials"}
        try:
            session = requests.post(endpoint, headers=header, data=data)
            session.raise_for_status()
            token = session.json().get("access_token")
            session.close()
            self.token = token
            return {"status": session.status_code, "token": self.token}
        except requests.exceptions.HTTPError as e:
            return {"status": e}

    def get_auth_header(self) -> Mapping[str, Any]:
        return {"Authorization": f"Bearer {self.token}", "Content-Type":"application/json", "X-Zuora-WSDL-Version": "107"}


# Basic full refresh stream
class ZuoraStream(Stream, ABC):
    
    def __init__(self, auth_header: dict, start_date: str, client_id: str, client_secret: str, is_sandbox: bool, **kwargs):
        self.auth_header = auth_header
        self.start_date = start_date
        self.client_id = client_id
        self.client_secret = client_secret
        self.is_sandbox = is_sandbox

    # Define URL_BASE
    @property
    def url_base(self) -> str:
        if self.is_sandbox == True:
            return "https://rest.apisandbox.zuora.com"
        else: 
            return "https://rest.zuora.com"


    







    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        pass

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        pass


    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        TODO: Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        yield {}


class Account(ZuoraStream):

    obj = "Account"
    primary_key = "id"

    """ def some_func(self, obj: str):
        return print(self.submit_data_query_job(zuora_object=obj, start_date=self.start_date)) """

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
        zuora_object: str = None,
    ) -> Iterable[Mapping[str, Any]]:
        """
        This method should be overridden by subclasses to read records based on the inputs
        """
        return print(self.submit_data_query_job(zuora_object=self.obj, start_date=self.start_date))


    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "account"



# Basic incremental stream
class IncrementalZuoraStream(ZuoraStream, ABC):
    """
    TODO fill in details of this class to implement functionality related to incremental syncs for your connector.
         if you do not need to implement incremental sync for any streams, remove this class.
    """

    # TODO: Fill in to checkpoint stream reads after N records. This prevents re-reading of data if the stream fails for any reason.
    state_checkpoint_interval = None

    @property
    def cursor_field(self) -> str:
        """
        TODO
        Override to return the cursor field used by this stream e.g: an API entity might always use created_at as the cursor field. This is
        usually id or date based. This field's presence tells the framework this in an incremental stream. Required for incremental.

        :return str: The name of the cursor field.
        """
        return []

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest record and
        the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
        """
        return {}


class Employees(IncrementalZuoraStream):
    """
    TODO: Change class name to match the table/data source this stream corresponds to.
    """

    # TODO: Fill in the cursor_field. Required.
    cursor_field = "start_date"

    # TODO: Fill in the primary key. Required. This is usually a unique field in the stream, like an ID or a timestamp.
    primary_key = "employee_id"

    def path(self, **kwargs) -> str:
        """
        TODO: Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/employees then this should
        return "single". Required.
        """
        return "employees"

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        """
        TODO: Optionally override this method to define this stream's slices. If slicing is not needed, delete this method.

        Slices control when state is saved. Specifically, state is saved after a slice has been fully read.
        This is useful if the API offers reads by groups or filters, and can be paired with the state object to make reads efficient. See the "concepts"
        section of the docs for more information.

        The function is called before reading any records in a stream. It returns an Iterable of dicts, each containing the
        necessary data to craft a request for a slice. The stream state is usually referenced to determine what slices need to be created.
        This means that data in a slice is usually closely related to a stream's cursor_field and stream_state.

        An HTTP request is made for each returned slice. The same slice can be accessed in the path, request_params and request_header functions to help
        craft that specific request.

        For example, if https://example-api.com/v1/employees offers a date query params that returns data for that particular day, one way to implement
        this would be to consult the stream state object for the last synced date, then return a slice containing each date from the last synced date
        till now. The request_params function would then grab the date from the stream_slice and make it part of the request by injecting it into
        the date query param.
        """
        raise NotImplementedError("Implement stream slices or delete this method!")


# Basic Connections Check
class SourceZuora(AbstractSource):
    
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, any]:

        """
        Testing connection availability for the connector.
        """
        client_id = config["client_id"]
        client_secret = config["client_secret"]
        is_sandbox = config["is_sandbox"]

        auth = ZuoraAuthenticator(client_id=client_id, client_secret=client_secret, is_sandbox=is_sandbox).generateToken()

        if auth["status"] == 200:
            return True, None
        else:
            return False, auth["status"]
        

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:

        """
        Mapping a input config of the user input configuration as defined in the connector spec.
        Defining streams to run.
        """
        inst = ZuoraAuthenticator(client_id=config["client_id"], client_secret=config["client_secret"], is_sandbox=config["is_sandbox"])
        auth = inst.generateToken()
        auth_header = inst.get_auth_header()

        args = {
            "authenticator": auth['token'],
            "auth_header": auth_header,
            "start_date": config["start_date"],
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "is_sandbox": config["is_sandbox"]
        }
        return [
            Account(**args)
        ]

