#
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
#


import json as j
from datetime import datetime
from math import ceil
from typing import Dict, Iterable, List, Mapping

import pendulum
import requests

from .auth import ZuoraAuthenticator


class ZoqlExport:

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
        if self.is_sandbox:
            return "https://rest.apisandbox.zuora.com"
        else:
            return "https://rest.zuora.com"

    # MAKE QUERY: for data_query_job

    @staticmethod
    def _make_dq_query(obj: str, date_field: str, start_date: str, end_date: str = None) -> Dict:
        # POTENTIALLY COULD BE REPLACED WITH request_parameters()

        end_date = pendulum.now().to_datetime_string() if end_date is None else end_date
        query = {
            "compression": "NONE",
            "output": {"target": "S3"},
            "outputFormat": "JSON",
            "query": f"select * from {obj} where {date_field} >= TIMESTAMP '{start_date}' and {date_field} <= TIMESTAMP '{end_date}'",
        }
        return query

    # SUBMIT: data_query_job using data_query
    def _submit_dq_job(self, dq_query: Dict, token_retry_max: int = 2) -> str:
        self.token_retry_max = token_retry_max

        token_retry = 0
        while token_retry <= self.token_retry_max:
            try:
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
                    print("\nRefreshing Token...\n")
                    self.authenticator = ZuoraAuthenticator(self.is_sandbox).generateToken(self.client_id, self.client_secret).get("header")
                    continue
                else:
                    raise Exception(e)

    # CHECK: the submited data_query_job status
    def _check_dq_job_status(self, dq_job_id: str, token_retry_max: int = 2) -> requests.Response:
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
                    print("\n", {"errorMessage": res["data"]["errorMessage"]}, "\n")
                    return iter(())
            except requests.exceptions.HTTPError as e:
                # if we got 401 HTTPError: Unauthorised, because of invalid or expired token
                # we refresh it and replace with the new token
                token_retry += 1
                if token_retry <= self.token_retry_max:
                    print("\nRefreshing Token...\n")
                    self.authenticator = ZuoraAuthenticator(self.is_sandbox).generateToken(self.client_id, self.client_secret).get("header")
                    continue
                else:
                    raise Exception(e)
        return res

    # GET: data_query_job result
    def _get_data_from_dq_job(self, response: requests.Response) -> List:
        get_dq_job_data = requests.get(response["data"]["dataFile"])
        get_dq_job_data.raise_for_status()
        data = [j.loads(line) for line in get_dq_job_data.text.splitlines()]
        return data or []

    # Warpper function for `Query > Submit > Check > Get`
    def _get_data(self, obj: str, date_field: str, start_date: str, end_date: str = None) -> Iterable[Mapping]:
        query = self._make_dq_query(obj=obj, date_field=date_field, start_date=start_date, end_date=end_date)
        # print(f"\nQUERY: {query}\n")
        submit = self._submit_dq_job(query)
        check = self._check_dq_job_status(submit)
        get = self._get_data_from_dq_job(check)
        yield from get

    # Warper for _get_data using date-slices as pages
    def _get_data_with_date_slice(
        self, obj: str, date_field: str, start_date: str, window_days: int, end_date: str = None
    ) -> Iterable[Mapping]:
        # Parsing input dates
        s = pendulum.parse(start_date)
        tz = self._get_tz(s)
        # If there is no `end_date` as input - use now()
        e = pendulum.parse(pendulum.now().to_datetime_string()) if end_date is None else pendulum.parse(end_date)
        # check end_date bigger than start_date
        if s >= e:
            return {"Error": "'End Date' should be bigger than 'Start Date'!"}
        else:
            # Get n of date-slices
            n = self._get_n_slices(s, e, window_days)
            # initiating slice_start/end for date slice
            slice_start = s.to_datetime_string() + tz
            # if slice_end is bigger than the input end_date, switch to the end_date
            slice_end = self._check_end_date(self._next_slice_end_date(slice_start, window_days), e) + tz
            # For multiple date-slices
            if n > 1:
                while n > 0:
                    yield from self._get_data(obj, date_field, slice_start, slice_end)
                    # make next date-slice
                    slice_start = slice_end
                    # if next date-slice end_date is bigger than the input end_date, we switch to the end_date
                    slice_end = self._check_end_date(self._next_slice_end_date(slice_end, window_days), e) + tz
                    # Modify iterator
                    n -= 1
                    # print(n)
            else:
                # For 1 date-slice
                yield from self._get_data(obj, date_field, slice_start, slice_end)

    @staticmethod
    def _check_end_date(slice_end_date, global_end_date: str) -> str:
        return global_end_date.to_datetime_string() if pendulum.parse(slice_end_date) > global_end_date else slice_end_date

    @staticmethod
    def _get_n_slices(start_date: datetime, end_date: datetime, window_days: int):
        # case where we have 1 sec difference between start and end dates would produce 0 slices, so return 1 instead
        d = pendulum.period(start_date, end_date).in_days()
        return 1 if ceil(d / window_days) <= 0 else ceil(d / window_days)

    @staticmethod
    def _next_slice_end_date(end_date: str, window_days: int):
        # potentially could be replaced with next_page_token
        format = "YYYY-MM-DD HH:mm:ss Z"
        return pendulum.from_format(end_date, format).add(days=window_days).to_datetime_string()

    @staticmethod
    def _get_tz(start_date: datetime) -> str:
        return " +00:00" if start_date.tzname() == "UTC" else f" {start_date.tzname()}"
