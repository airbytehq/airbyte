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

import json
from typing import Any, Dict, Mapping

import pendulum
from source_zuora.source import (
    ZuoraDescribeObject,
    ZuoraGetJobResult,
    ZuoraJobStatusCheck,
    ZuoraListObjects,
    ZuoraObjectsBase,
    ZuoraSubmitJob,
)
from source_zuora.zuora_auth import ZuoraAuthenticator


# Method to get url_base from config input
def get_url_base(is_sandbox: bool = False) -> str:
    url_base = "https://rest.zuora.com"
    if is_sandbox:
        url_base = "https://rest.apisandbox.zuora.com"
    return url_base


def get_config(config_path: str) -> Mapping[str, Any]:
    """
    Get the config from /test_input
    """
    with open(config_path, "r") as f:
        return json.loads(f.read())


def client(config: Dict):
    """
    Create client by extending config dict with authenticator and url_base
    """
    url_base = get_url_base(config["is_sandbox"])
    authenticator = ZuoraAuthenticator(
        token_refresh_endpoint=f"{url_base}/oauth/token",
        client_id=config["client_id"],
        client_secret=config["client_secret"],
        refresh_token=None,  # Zuora doesn't have Refresh Token parameter.
    )
    config["authenticator"] = authenticator
    config["url_base"] = url_base
    return config


class TestZuora:
    """
    This test class provides set of tests for custom classes of the Airbyte Zuora connector.
    The test is based on input so feel free to change the input parameters.

    Class attributes that marked with (!) are must have.

    ::  (!) config - is the Dict with authenticator and url_base parameters.
    ::  (!) test_stream - the name of the Zuora Object
    ::  (!) test_cursor_field - basicaly the date field which allow to filter and query the data from Zuora Test Object,
            default is 'updateddate' it's available for the most of the Zuora Objects, some uses 'createddate',
            check this before set this parameter.
    ::  (!) test_schema_fields - the list of fields / Columns available for the test_stream,
            check this before set this parameter.
    ::  (!) test_fields_schema_types - basically the prepared expected output for the get_json_schema() for the test_stream,
            we expect if the schema discovery is correctly performed, we should have this types of fields in the output,
            than connector should be able to normalize data as expected.

    Issues that could potentially may take place:
    ::  If the any of the tests fails,
        - check the input parameters first,
        - start_date in the secrets/config.json, this should be valid date range where data is 100% available to be read.
        - availability of the test_stream in the Zuora Account and your Subscription Plan.
        - check other errors from the test output.
    """

    # create client
    config = client(config=get_config("secrets/config.json"))

    # Define common test input
    test_stream = "account"
    test_cursor_field = "updateddate"
    test_schema_fields = ["id", "creditbalance", "allowinvoiceedit"]
    test_fields_schema_types = {
        "id": {"type": ["string", "null"]},
        "creditbalance": {"type": ["number", "null"]},
        "allowinvoiceedit": {"type": ["boolean", "null"]},
    }

    def _prepare_date_slice(self):
        """
        Helper method for other tests,
        makes test_date_slice to use within another tests.
        As well as we test the ZuoraObjectsBase.to_datetime_str method for correct datetime formating needed for the query to run.
        """
        start_date = ZuoraObjectsBase.to_datetime_str(pendulum.parse(self.config["start_date"]).astimezone())
        end_date = ZuoraObjectsBase.to_datetime_str(pendulum.now().astimezone())
        test_date_slice = {"start_date": start_date, "end_date": end_date}
        return test_date_slice

    def test_list_all_zuora_objects(self):
        """
        Test retrieves all the objects (streams) available from Zuora Account and checks if test_stream is in the list.
        """
        zuora_objects_list = ZuoraListObjects(self.config).read_records(sync_mode=None)
        assert self.test_stream in zuora_objects_list

    def test_get_json_schema(self):
        """
        Test of getting schema from Zuora endpoint, check converted JsonSchema Types are correct
        """
        schema = list(ZuoraDescribeObject(self.test_stream, config=self.config).read_records(sync_mode=None))
        schema = {key: d[key] for d in schema for key in d}

        # Filter the schema up to the test_schema_fields
        output_converted_schema_types = {key: value for key, value in schema.items() if key in self.test_schema_fields}

        # Return True if all is correct
        assert self.test_fields_schema_types == output_converted_schema_types

    def test_query(self):
        """
        The ZuoraObjectsBase.query() works with date_slices as input,
        we test if date_slices are formed and passed correctly.
        """
        # Prepare date_slice
        test_date_slice = self._prepare_date_slice()

        # Making example query using input
        example_query = f"""
            select * from {self.test_stream} where
            {self.test_cursor_field} >= TIMESTAMP '{test_date_slice.get("start_date")}' and
            {self.test_cursor_field} <= TIMESTAMP '{test_date_slice.get("end_date")}'
            """

        # Making test query using query() method
        test_query = ZuoraObjectsBase.query(
            self, stream_name=self.test_stream, cursor_field=self.test_cursor_field, date_slice=test_date_slice
        )

        # If the query is correctly build using connector class return True
        assert example_query == test_query

    def test_submit_job(self):
        """
        Test submits the job to the server and returns the `job_id` as confirmation that the job was submitted successfully.
        """

        # Prepare date_slice
        test_date_slice = self._prepare_date_slice()

        # Submitting the job to the server
        job_id = ZuoraSubmitJob(
            ZuoraObjectsBase.query(self, stream_name=self.test_stream, cursor_field=self.test_cursor_field, date_slice=test_date_slice),
            self.config,
        ).read_records(sync_mode=None)

        # Return True if we have submited job_id
        assert len(list(job_id)) > 0

    def test_check_job_status(self):
        """
        Test checks submited job for status, if status is "completed" job_data_url will contain URL for jsonl dataFile,
        Otherwise, if the status of the job is in ["failed", "canceled", "aborted"] it will raise the error message to the output,
        describing what type of error occured.
        """

        # Prepared date_slice
        test_date_slice = self._prepare_date_slice()

        # Submiting a job first
        job_id = ZuoraSubmitJob(
            ZuoraObjectsBase.query(self, stream_name=self.test_stream, cursor_field=self.test_cursor_field, date_slice=test_date_slice),
            self.config,
        ).read_records(sync_mode=None)

        # checking iteratively if the job is completed, then return the URL with jsonl datafile
        job_data_url = ZuoraJobStatusCheck(list(job_id)[0], self.config).read_records(sync_mode=None)

        # Return True if there is a URL leading to a file
        assert "https://" in list(job_data_url)[0]

    def test_get_job_result(self):
        """
        Test reads the dataFile from URL of submited, checked and successfully completed job.
        """

        # Prepared date_slice
        test_date_slice = self._prepare_date_slice()

        # Submiting a job first
        job_id = ZuoraSubmitJob(
            ZuoraObjectsBase.query(self, stream_name=self.test_stream, cursor_field=self.test_cursor_field, date_slice=test_date_slice),
            self.config,
        ).read_records(sync_mode=None)

        # checking iteratively if the job is completed, then return the URL with jsonl datafile
        job_data_url = ZuoraJobStatusCheck(list(job_id)[0], self.config).read_records(sync_mode=None)

        # read records from completed job
        job_result = ZuoraGetJobResult(list(job_data_url)[0]).read_records(sync_mode=None)
        # Return True if we have successfully read records from completed job
        assert len(list(job_result)) > 0
