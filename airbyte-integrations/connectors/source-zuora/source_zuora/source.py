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
from typing import Any, Callable, Iterable, List, Mapping, MutableMapping, Optional, Tuple

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
from source_zuora.zuora_auth import ZuoraAuthenticator


# Basic full refresh stream
class ZuoraStream(Stream, ABC):
    
    def __init__(self, authenticator: str, auth_header: dict, start_date: str, client_id: str, client_secret: str, is_sandbox: bool, **kwargs):
        self.auth_header = auth_header
        self.start_date = start_date
        # self.client_id = client_id
        # self.client_secret = client_secret
        self.is_sandbox = is_sandbox
        self.token = authenticator
        # self.new_token = refreshed_token

    # Define base url from is_sandbox arg.
    @property
    def url_base(self) -> str:
        if self.is_sandbox == True:
            return "https://rest.apisandbox.zuora.com"
        else: 
            return "https://rest.zuora.com"

    # Define limit in days for the fetch
    limit_days = 200

    # Define general primary key
    primary_key = "id"

    # SUBMIT: data_query_job
    def _submit_dq_job(self, z_obj: str, start_date: str, end_date: str = None, token_retry_max: int = 2) -> str:
        self.start_date = start_date
        self.end_date = pendulum.now().to_datetime_string() if end_date is None else end_date
        self.token_retry_max = token_retry_max

        endpoint = f"{self.url_base}/query/jobs"
        header = self.auth_header
        query = {
            "compression": "NONE",
            "output": {"target": "S3"},
            "outputFormat": "JSON",
            "query": f"select * from {z_obj} where UpdatedDate >= TIMESTAMP '{self.start_date}' and UpdatedDate <= TIMESTAMP '{self.end_date}'"
        }

        # make initial submition
        token_retry = 0
        while token_retry <= self.token_retry_max:
            try: 
                submit_job = requests.post(url=endpoint, headers=header, json=query)
                submit_job.raise_for_status()
                submit_job = submit_job.json()["data"]["id"]
                # print({"submit job_id": submit_job})
                return submit_job
            except requests.exceptions.HTTPError as e:
                # if we got 401 HTTPError: Unauthorised, because of invalid or expired token
                # we refresh it and replace with the new token
                token_retry += 1
                if token_retry <= self.token_retry_max:
                    print(f"Refreshing Token...")
                    self.generateToken()
                    header["Authorization"] = f"Bearer {self.token}"
                    continue
                raise Exception(e)

    # CHECK: the submited data_query_job status 
    def _check_dq_job_status(self, dq_job_id: str, check_interval: int = 1, token_retry_max: int = 2) -> requests.Response:
        self.dq_job_id = dq_job_id
        self.token_retry_max = token_retry_max

        endpoint = f"{self.url_base}/query/jobs/{self.dq_job_id}"
        header = self.auth_header

        status = None
        token_retry = 0
        
        while status != "completed":
            try:
                # time.sleep(check_interval)
                res = requests.get(url=endpoint, headers=header)
                res.raise_for_status()
                res = res.json()
                status = res["data"]["queryStatus"]
                # print({"status job_id": self.data_query_job_id, "status": status})
                    
                if status == "failed":
                    print({"errorMessage": res["data"]["errorMessage"]})
                    return iter(())
                    # Wait interval before next check
                
            except requests.exceptions.HTTPError as e:
                # if we got 401 HTTPError: Unauthorised, because of invalid or expired token
                # we refresh it and replace with the new token
                token_retry += 1
                if token_retry <= self.token_retry_max:
                    print(f"Refreshing Token...")
                    # self.token = self.new_token
                    header["Authorization"] = f"Bearer {self.token}"
                    continue
                else:
                    raise Exception(e)
        return res

    # GET: data_query_job result
    def _get_data_from_dq_job(self, response: object) -> List:

        # print({"data job_id": response["data"]["id"]})
        get_dq_job_data = requests.get(response["data"]["dataFile"])
        get_dq_job_data.raise_for_status()
        data = [j.loads(l) for l in get_dq_job_data.text.splitlines()]
        return data or []

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

    # Warpper function for `Submit > Check > Get`
    def _get_data(self, z_obj: str, start_date: str, end_date: str = None) -> Iterable[Mapping]:
        submit = self._submit_dq_job(z_obj=z_obj, start_date=start_date, end_date=end_date)
        check = self._check_dq_job_status(submit)
        get = self._get_data_from_dq_job(check)
        yield from get

    # Warper for _get_data using date-slices as pages
    def _get_data_with_date_slice(self, z_obj: str, start_date: str, end_date: str = None, window_days: int = 10) -> Iterable[Mapping]:

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
                    yield from self._get_data(z_obj, iter_s, iter_e)

                    # make next date-slice
                    iter_s = iter_e
                    iter_e = self._next_slice_end_date(iter_e, window_days)

                    # if iter_e is bigger than the input end_date, we switch to the end_date
                    iter_e = self._check_end_date(iter_e, e)

                    # Modify iterator
                    n -= 1
            else:
                # if we have just only 1 date-slice to fetch
                print(f"\nDate Range Chunk: {iter_s} -- {iter_e}\n")
                yield from self._get_data(z_obj, iter_s, iter_e)
    
    def read_records(
        self, 
        # sync_mode: SyncMode, 
        # cursor_field: List[str] = None, 
        # stream_slice: Mapping[str, Any] = None, 
        # stream_state: Mapping[str, Any] = None,
        **kwargs
    ) -> Iterable[Mapping]:
        yield from self._get_data_with_date_slice(z_obj=self.name, start_date=self.start_date, window_days=self.limit_days)


class Account(ZuoraStream):
    cursor_field = "updated_at"

class Order(ZuoraStream):
    cursor_field = "updated_at"






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
            "is_sandbox": config["is_sandbox"],
            #  "refreshed_token": inst.generateToken()
        }
        return [
            Account(**args)
        ]

