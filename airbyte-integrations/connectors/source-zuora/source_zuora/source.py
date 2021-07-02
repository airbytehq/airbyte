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
from datetime import datetime
from typing import Any, Callable, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Dict

import json as j
# import time
# from itertools import chain
from math import ceil
import requests
import pendulum

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from source_zuora.auth import ZuoraAuthenticator


class ZuoraDataQuery(Stream, ABC):

    """
    # TODO: Add the description about the Daat Query Method + Links
    # TODO: Add description about class methods 
    """

    def __init__(self, authenticator: Dict, start_date: str, window_in_days: int, client_id: str, client_secret: str, is_sandbox: bool):
        self.start_date = start_date
        self.window_in_days = window_in_days
        self.client_id = client_id
        self.client_secret = client_secret
        self.is_sandbox = is_sandbox
        self.authenticator = authenticator

    # Define base url from is_sandbox arg.
    @property
    def url_base(self) -> str:
        if self.is_sandbox == True:
            return "https://rest.apisandbox.zuora.com"
        else: 
            return "https://rest.zuora.com"


    # MAKE QUERY: for data_query_job
    @staticmethod
    def _make_dq_query(obj: str, start_date: str, end_date: str = None) -> Dict:
        end_date = pendulum.now().to_datetime_string() if end_date is None else end_date
        query = {
            "compression": "NONE",
            "output": {"target": "S3"},
            "outputFormat": "JSON",
            "query": f"select * from {obj} where UpdatedDate >= TIMESTAMP '{start_date}' and UpdatedDate <= TIMESTAMP '{end_date}'"
        }
        return query

    # SUBMIT: data_query_job using data_query
    def _submit_dq_job(self, dq_query: Dict, token_retry_max: int = 2) -> str:
        # self.start_date = start_date
        #self.end_date = pendulum.now().to_datetime_string() if end_date is None else end_date
        self.token_retry_max = token_retry_max

        token_retry = 0
        while token_retry <= self.token_retry_max:
            try:
                # print(f"\nUSE TOKEN: {self.authenticator}")
                # make initial submition
                submit_job = requests.post(url=f"{self.url_base}/query/jobs", headers=self.authenticator, json=dq_query)
                submit_job.raise_for_status()
                submit_job = submit_job.json()["data"]["id"]
                return submit_job
            except requests.exceptions.HTTPError as e:
                # if we got 401 HTTPError: Unauthorised, because of invalid or expired token
                # we refresh it and replace `self.authenticator` with the new token
                token_retry += 1
                if token_retry <= self.token_retry_max:
                    # print(f"\nOLD TOKEN: {self.authenticator}")
                    print(f"Refreshing Token...")
                    self.authenticator = ZuoraAuthenticator(self.is_sandbox).generateToken(self.client_id, self.client_secret).get("header")
                    continue
                else:
                    raise Exception(e)                

    # CHECK: the submited data_query_job status 
    def _check_dq_job_status(self, dq_job_id: str, token_retry_max: int = 2) -> requests.Response:
        # self.dq_job_id = dq_job_id
        self.token_retry_max = token_retry_max
        token_retry = 0
        
        status = None
        while status != "completed":
            try:
                res = requests.get(url=f"{self.url_base}/query/jobs/{dq_job_id}", headers=self.authenticator)
                res.raise_for_status()
                res = res.json()
                status = res["data"]["queryStatus"]    
                if status == "failed":
                    print("\n",{"errorMessage": res["data"]["errorMessage"]},"\n")
                    return iter(())
            except requests.exceptions.HTTPError as e:
                # if we got 401 HTTPError: Unauthorised, because of invalid or expired token
                # we refresh it and replace with the new token
                token_retry += 1
                if token_retry <= self.token_retry_max:
                    print(f"Refreshing Token...")
                    self.authenticator = ZuoraAuthenticator(self.is_sandbox).generateToken(self.client_id, self.client_secret).get("header")
                    continue
                else:
                    raise Exception(e)
        return res

    # GET: data_query_job result
    def _get_data_from_dq_job(self, response: requests.Response) -> List:
        get_dq_job_data = requests.get(response["data"]["dataFile"])
        get_dq_job_data.raise_for_status()
        data = [j.loads(l) for l in get_dq_job_data.text.splitlines()]
        return data or []

    # Warpper function for `Query > Submit > Check > Get`
    def _get_data(self, obj: str, start_date: str, end_date: str = None) -> Iterable[Mapping]:
        query = self._make_dq_query(obj, start_date, end_date)
        submit = self._submit_dq_job(query)
        check = self._check_dq_job_status(submit)
        get = self._get_data_from_dq_job(check)
        yield from get

    # Warper for _get_data using date-slices as pages
    def _get_data_with_date_slice(self, obj: str, start_date: str, end_date: str = None, window_days: int = 10) -> Iterable[Mapping]:

        # Parsing input dates
        s = pendulum.parse(start_date)
        # If there is no `end_date` as input - use now()
        e = pendulum.parse(pendulum.now().to_datetime_string()) if end_date is None else pendulum.parse(end_date)

        # check end_date bigger than start_date
        if s >= e: 
            return {"Error": "'End Date' should be bigger than 'Start Date'!"}
        else:
            # Get n of date-slices
            n = self._get_n_date_slices(s, e, window_days)
            # initiating intermediate `start` and `end` for date slice
            iter_s = s.to_datetime_string()
            # if iter_e is bigger than the input end_date, switch to the end_date
            iter_e = self._check_end_date(s.add(days=window_days).to_datetime_string(), e)
            # If we have more than 1 date-slice to fetch
            if n > 1:
                # print(f"\nGetting data with {n} Chunks\n")
                while n > 0:
                    # print(f"\nDate-Slice: {iter_s} -- {iter_e}\n")
                    yield from self._get_data(obj, iter_s, iter_e)
                    # make next date-slice
                    iter_s = iter_e
                    iter_e = self._next_slice_end_date(iter_e, window_days)
                    # if iter_e is bigger than the input end_date, we switch to the end_date
                    iter_e = self._check_end_date(iter_e, e)
                    # Modify iterator
                    n -= 1
            else:
                # if we have just only 1 date-slice to fetch
                # print(f"\nDate Range Chunk: {iter_s} -- {iter_e}\n")
                yield from self._get_data(obj, iter_s, iter_e)

    @staticmethod
    def _check_end_date(slice_end_date, global_end_date: str) -> str:
        if pendulum.parse(slice_end_date) > global_end_date:
            slice_end_date = global_end_date.to_datetime_string()
        return slice_end_date

    @staticmethod
    def _get_n_date_slices(start_date: datetime, end_date: datetime, window_days: int):
        d = pendulum.period(start_date,end_date).in_days()
        # case when we have the 1 sec more for end_date would produce n = 0, so put 1 instead
        n = 1 if ceil(d/window_days) <= 0 else ceil(d/window_days)
        return n

    @staticmethod
    def _next_slice_end_date(end_date: str, window_days: int):
        return pendulum.parse(end_date).add(days=window_days).to_datetime_string()


class IncrementalZuoraStream(ZuoraDataQuery):

    # Define general primary key
    primary_key = "id"

    # Define cursor filed for incremental refresh
    cursor_field = "updateddate"

    # setting limit of the date-slice for the data query job
    @property
    def limit_days(self) -> int:
        return self.window_in_days

    # setting checkpoint interval to the limit of date-slice
    state_checkpoint_interval = limit_days

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        return {self.cursor_field: max(latest_record.get(self.cursor_field, ""), current_stream_state.get(self.cursor_field, ""))}

    def read_records(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Mapping]:
        # initialise 1start_date1 to determine the stream_state or start_date from user's input
        # if stream_state is missing, we will use the start-date from config for a full refresh
        start_date = stream_state.get(self.cursor_field) if stream_state else self.start_date
        yield from self._get_data_with_date_slice(self.name, start_date, window_days=self.limit_days)


class Account(IncrementalZuoraStream):
    """THIS IS THE LINK FOR ACCOUNT DOCUMENTATION"""

class Orders(IncrementalZuoraStream):
    """THIS IS THE LINK FOR ORDERS DOCUMENTATION"""


# Basic Connections Check
class SourceZuora(AbstractSource):
    
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, any]:

        """
        Testing connection availability for the connector by granting the token.
        """

        auth = ZuoraAuthenticator(config["is_sandbox"]).generateToken(config["client_id"], config["client_secret"])
        print(auth)
        if auth.get("status") == 200:
            return True, None
        else:
            return False, auth["status"]

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:

        """
        Mapping a input config of the user input configuration as defined in the connector spec.
        Defining streams to run.
        """

        auth = ZuoraAuthenticator(config["is_sandbox"]).generateToken(config["client_id"], config["client_secret"])

        # Remove this block once finished
        """ 
        fake_auth = {
                    "Authorization": f"Bearer some_fake_token", 
                    "Content-Type":"application/json", 
                    "X-Zuora-WSDL-Version": "107",
                }
        """
        #

        args = {
            # "authenticator": fake_auth,
            "authenticator": auth.get("header"),
            "start_date": config["start_date"],
            "window_in_days": config["window_in_days"],
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "is_sandbox": config["is_sandbox"],
        }
        return [
            Account(**args),
            Orders(**args),
        ]

