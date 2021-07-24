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
from datetime import datetime, timedelta
from math import ceil
from typing import Dict, Iterable, List

import pendulum
import requests
from airbyte_cdk import AirbyteLogger

from .zuora_auth import ZuoraAuthenticator
from .zuora_errors import ZOQLQueryCannotProcessObject, ZOQLQueryFailed, ZOQLQueryFieldCannotResolve


class ZoqlExportClient:

    """
    # TODO: Add the description about the ZOQL EXPORT + Links
    """

    logger = AirbyteLogger()

    def __init__(self, authenticator: Dict, url_base: str, **config: Dict):
        self.authenticator = authenticator
        self.url_base = url_base
        self.start_date = config["start_date"]
        self.window_in_days = config["window_in_days"]
        self.client_id = config["client_id"]
        self.client_secret = config["client_secret"]
        self.is_sandbox = config["is_sandbox"]
        self.retry_max = 3  # Max number of retries for make_request method

    def make_request(self, method: str = "GET", url: str = None, payload: Dict = None) -> requests.Response:
        """
        try/except request wraper with handling errors
        """

        retry = 0
        while retry <= self.retry_max:
            try:
                request = requests.request(method=method, url=url, headers=self.authenticator, json=payload)
                request.raise_for_status()
                return request
            except requests.exceptions.HTTPError as e:
                retry += 1
                if retry <= self.retry_max:
                    self.handle_requests_exceptions(e)
                    continue
                else:
                    raise Exception(e)

    def make_query(
        self, q_type: str = "select", obj: str = None, date_field: str = None, start_date: str = None, end_date: str = None
    ) -> Dict:
        """
        Make the query for dependent methods like:
        submit_job, check_job_status, zuora_list_streams, zuora_get_json_schema
        """
        # Define base query parameters
        base_query = {"compression": "NONE", "output": {"target": "S3"}, "outputFormat": "JSON"}

        if q_type == "select":
            end_date = self.to_datetime_str(pendulum.now().astimezone()) if not end_date else end_date
            base_query[
                "query"
            ] = f"select * from {obj} where {date_field} >= TIMESTAMP '{start_date}' and {date_field} <= TIMESTAMP '{end_date}'"
        elif q_type == "describe":
            base_query["query"] = f"DESCRIBE {obj}"
        elif q_type == "show_tables":
            base_query["query"] = "SHOW TABLES"
        return base_query

    def submit_job(self, dq_query: Dict) -> str:
        """
        Method to submit the query job for the Zuora
        """
        submit_job = self.make_request(method="POST", url=f"{self.url_base}/query/jobs", payload=dq_query)
        return submit_job.json()["data"]["id"]

    def check_job_status(self, dq_job_id: str) -> Dict:
        """
        Method to check submited query job for the Zuora using id.
        There could be next statuses: ["completed", "in_progress", "failed", "canceled", "aborted"]
        """

        # Define the job error statuses
        errors = ["failed", "canceled", "aborted"]
        # Error msg: the cursor_field cannot be resolved
        cursor_error = "Column 'updateddate' cannot be resolved"
        # Error msg: cannot process object
        obj_read_error = "failed to process object"

        status = None
        success = "completed"
        while status != success:
            response = self.make_request(url=f"{self.url_base}/query/jobs/{dq_job_id}")
            job_check = response.json()
            status = job_check["data"]["queryStatus"]
            if status in errors and cursor_error in job_check["data"]["errorMessage"]:
                raise ZOQLQueryFieldCannotResolve
            elif status in errors and obj_read_error in job_check["data"]["errorMessage"]:
                raise ZOQLQueryCannotProcessObject
            elif status in errors:
                raise ZOQLQueryFailed(response)
        return job_check

    def get_job_data(self, response: requests.Response) -> List:
        """
        Get actual output from submited data query job, when it's completed, using the link inside status job response
        """

        job_data = requests.get(response["data"]["dataFile"])
        job_data.raise_for_status()
        data = [j.loads(line) for line in job_data.text.splitlines()]
        return data or []

    def get_data(
        self, q_type: str = "select", obj: str = None, date_field: str = None, start_date: str = None, end_date: str = None
    ) -> Iterable:
        """
        Convinient wraper for `Make Query > Submit > Check > Get` operations
        """

        query = self.make_query(q_type, obj, date_field, start_date, end_date)
        submit = self.submit_job(query)
        check = self.check_job_status(submit)
        get = self.get_job_data(check)
        yield from get

    def get_data_with_date_slice(
        self, q_type: str, obj: str, date_field: str, start_date: str, window_days: int, end_date: str = None
    ) -> Iterable:
        """
        Wraper for get_data using date-slices as pages, to overcome:
        rate limits, data-job size limits, data-job performance issues on the server side.
        """

        # Parsing input dates
        start: datetime = pendulum.parse(start_date)
        # If there is no `end_date` as input - use now()
        end: datetime = pendulum.parse(end_date).astimezone() if end_date else pendulum.now().astimezone()
        # Get n of date-slices
        n_slices = self.get_n_slices(start, end, window_days)

        # initiating slice_start/end for date slice
        slice_start: datetime = start
        # if slice_end is bigger than the input end_date, switch to the end_date
        slice_end: datetime = min(start + timedelta(days=window_days), end)
        while n_slices > 0:
            yield from self.get_data(q_type, obj, date_field, self.to_datetime_str(slice_start), self.to_datetime_str(slice_end))
            slice_start = slice_end
            slice_end = min(slice_end + timedelta(days=window_days), end)
            print(f"slice: \n{n_slices}")
            print(f"start: \n{self.to_datetime_str(slice_start)}")
            print(f"end: \n{self.to_datetime_str(slice_end)}\n")
            n_slices -= 1

    @staticmethod
    def to_datetime_str(date: datetime) -> str:
        """
        The output from this method should be formated as follows:
        :: "YYYY-mm-dd HH:mm:ss Z"
        :: example: '2021-07-15 07:45:55 -07:00'
        """
        return f"{date.to_datetime_string()} {date.strftime('%Z')}"

    @staticmethod
    def get_n_slices(start_date: datetime, end_date: datetime, window_days: int) -> int:
        """
        Get n of date-slices needed to fetch the data.
        Case where we have 1 sec difference between start and end dates would produce 0 slices, so return 1 instead
        """
        d = pendulum.period(start_date, end_date).in_days()
        return 1 if ceil(d / window_days) <= 0 else ceil(d / window_days)

    def convert_schema_types(self, schema: List[Dict]) -> Dict:
        """
        Takes the List of Dict from raw_schema with Zuora Data Types,
        converts Zuora DataTypes to JSONSchema Types
        Outputs the Dict that could be set inside of
        ::properties of json_schema.
        """

        casted_schema_types = {}
        for field in schema:
            if field.get("type") in ["decimal(22,9)", "integer", "number", "int", "bigint", "smallint", "timestamp"]:
                field_type = ["number", "null"]
            elif field.get("type") in ["date", "datetime", "timestamp with time zone", "picklist", "text", "varchar"]:
                field_type = ["string", "null"]
            elif field.get("type") in ["zoql", "binary", "json", "xml", "blob"]:
                field_type = ["object", "null"]
            elif field.get("type") in ["list", "array"]:
                field_type = ["array", "null"]
            elif field.get("type") in ["boolean", "bool"]:
                field_type = ["boolean", "null"]
            else:
                # if there is something else we don't cover, cast it as string
                field_type = ["string", "null"]
            casted_schema_types.update(**{field.get("field"): {"type": field_type}})
        return casted_schema_types

    def zuora_get_json_schema(self, obj: str) -> Dict:
        """
        Pull out the Zuora Object's (stream) raw data-types,
        converts them into JsonSchema types,
        outputs the ready to go ::properties entries for the stream.
        """

        self.logger.info(f"Getting schema information for {obj}")
        raw_data_types = self.get_data(q_type="describe", obj=obj)
        raw_schema = [{"field": field["Column"], "type": field["Type"]} for field in raw_data_types]
        return self.convert_schema_types(raw_schema)

    def zuora_list_streams(self) -> List:
        """
        Get the list of Zuora Objects (streams) from Zuora account
        """

        self.logger.info("Retrieving the list of available Objects from Zuora")
        zuora_stream_names = self.get_data(q_type="show_tables")
        return [name["Table"] for name in zuora_stream_names]

    def handle_requests_exceptions(self, exception: requests.RequestException):

        """
        Method to handle exceptions for the make_request
        """

        exception_code = exception.response.status_code
        # print(exception_code)
        if exception_code in [500, 404]:
            # Bad Request - Server declined the request
            self.logger.error(f"Bad URL - please check the link, {exception}")
        elif exception_code == 400:
            # Bad Request - Server declined the request
            self.logger.error(f"Bad Request, please check the url query parameters, {exception}")
        elif exception_code == 401:
            # Unauthorised or Invalid Token
            self.logger.error(f"Unauthorised or Expired/Invalid Token, {exception}")
            # Attempt to refresh the token
            self.authenticator = ZuoraAuthenticator(self.is_sandbox).generateToken(self.client_id, self.client_secret).get("header")
            self.logger.info("Token is Refreshed")
        else:
            self.logger.fatal(f"Unrecognised Error Occured, please check traceback {exception}")
