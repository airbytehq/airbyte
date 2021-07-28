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
from source_zuora.zuora_auth import ZuoraAuthenticator
from source_zuora.source import ( 
    ZuoraObjectsBase,
    ZuoraListObjects, 
    ZuoraDescribeObject, 
    ZuoraSubmitJob, 
    ZuoraJobStatusCheck, 
    ZuoraGetJobResult,
)


# Method to get url_base from config input
def get_url_base(is_sandbox: bool = False) -> str:
    url_base = "https://rest.zuora.com"
    if is_sandbox:
        url_base = "https://rest.apisandbox.zuora.com"
    return url_base

# Method to read the config from test/input
def get_config() -> Mapping[str, Any]:
    """
    Get the config from /test_input
    """
    with open("secrets/config.json", "r") as f:
        return json.loads(f.read())

# creates client with config
def client(config: Dict = get_config()):
    url_base = get_url_base(config['is_sandbox'])
    authenticator = ZuoraAuthenticator(
        token_refresh_endpoint = f"{url_base}/oauth/token",
        client_id = config["client_id"],
        client_secret = config["client_secret"], 
        refresh_token = None, # Zuora doesn't have Refresh Token parameter.
    )
    config["authenticator"] = authenticator
    config["url_base"] = url_base
    return config


class TestClass:
    """
    This test class provides set of tests for custom classes of the Airbyte Zuora connector.
    The test is based on input so feel free to change the input parameters.
    """

    # create client
    config = client()

    # Define Test input
    test_stream = "account"
    test_cursor_field = "updateddate"
    test_schema_fields = ["id", "creditbalance", "allowinvoiceedit"]
    test_fields_schema_types = {
        "id": {'type': ['string', 'null']},
        "creditbalance" : {'type': ['number', 'null']},
        "allowinvoiceedit": {'type': ['boolean', 'null']},
        }

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
        schema = list(ZuoraDescribeObject(self.test_stream, config = self.config).read_records(sync_mode=None))
        schema = {key: d[key] for d in schema for key in d}

        # Filter the schema up to the test_schema_fields
        output_converted_schema_types = {key: value for key, value in schema.items() if key in self.test_schema_fields}

        # Return True if all is correct
        assert self.test_fields_schema_types == output_converted_schema_types

    def test_to_datetime_str(self):
        """
        Test converting ZuoraObjectsBase.to_datetime_str works correctly
        """
        # Check input in different format
        test_date = pendulum.parse(self.config["start_date"]).astimezone()
        is_correct_input = True if test_date.strftime("%Y-%m-%dT%H:%M:%S%Z") else False

        # Check output in different format
        test_output = ZuoraObjectsBase.to_datetime_str(test_date)
        is_correct_output = True if pendulum.from_format(test_output, "YYYY-MM-DD HH:mm:ss Z") else False

        # If both are correct return True
        assert is_correct_input and is_correct_output

    def test_query(self):
        """
        The ZuoraObjectsBase.query() works with date_slices as input, we test if date_slices are passed correctly
        
        """
        start_date = ZuoraObjectsBase.to_datetime_str(pendulum.parse(self.config["start_date"]).astimezone())
        end_date = ZuoraObjectsBase.to_datetime_str(pendulum.now().astimezone())
        test_date_slice = {"start_date": start_date, "end_date": end_date}

        # Making example query using input
        example_query = f"""
            select * from {self.test_stream} where 
            {self.test_cursor_field} >= TIMESTAMP '{start_date}' and 
            {self.test_cursor_field} <= TIMESTAMP '{end_date}'
            """

        # Making test query using query() method
        test_query = ZuoraObjectsBase.query(
            self, stream_name=self.test_stream, cursor_field=self.test_cursor_field, date_slice=test_date_slice
            )

        # If the query is correctly build using connector class return True
        assert example_query == test_query

    # TEST 5
    def test_submit_job(self):
        """
        Test submits the job to the server and returns the job_id as confimation that the job was submited
        """

        # Prepare date_slice
        start_date = ZuoraObjectsBase.to_datetime_str(pendulum.parse(self.config["start_date"]).astimezone())
        end_date = ZuoraObjectsBase.to_datetime_str(pendulum.now().astimezone())
        test_date_slice = {"start_date": start_date, "end_date": end_date}

        # Submitting the job to the server
        job_id = ZuoraSubmitJob(ZuoraObjectsBase.query(
            self, stream_name=self.test_stream, cursor_field=self.test_cursor_field, date_slice=test_date_slice
            ), self.config).read_records(sync_mode=None)

        # Return True if we have job_id
        assert len(list(job_id)) > 0
    
    # TEST 6
    def test_check_job_status(self):
        """
        Test checks submited job for status, if status is "completed" job_data_url will contain URL for jsonl dataFile,
        Otherwise, if the status of the job is in ["failed", "canceled", "aborted"] it will raise the error message to the output,
        describing what type of error occured.
        """

        # Prepare date_slice
        start_date = ZuoraObjectsBase.to_datetime_str(pendulum.parse(self.config["start_date"]).astimezone())
        end_date = ZuoraObjectsBase.to_datetime_str(pendulum.now().astimezone())
        test_date_slice = {"start_date": start_date, "end_date": end_date}

        # Submiting a job first
        job_id = ZuoraSubmitJob(ZuoraObjectsBase.query(
            self, stream_name=self.test_stream, cursor_field=self.test_cursor_field, date_slice=test_date_slice
            ), self.config).read_records(sync_mode=None)
        
        # checking iteratively if the job is completed, then return the URL with jsonl datafile
        job_data_url = ZuoraJobStatusCheck(list(job_id)[0], self.config).read_records(sync_mode=None)
        
        # Return True if there is a URL leading to a file
        assert "https://" in list(job_data_url)[0]

    # TEST 7
    def test_get_job_result(self):
        """
        Test reads the dataFile from URL of submited and successfully completed job.
        """

        # Prepare date_slice
        start_date = ZuoraObjectsBase.to_datetime_str(pendulum.parse(self.config["start_date"]).astimezone())
        end_date = ZuoraObjectsBase.to_datetime_str(pendulum.now().astimezone())
        test_date_slice = {"start_date": start_date, "end_date": end_date}

        # Submiting a job first
        job_id = ZuoraSubmitJob(ZuoraObjectsBase.query(
            self, stream_name=self.test_stream, cursor_field=self.test_cursor_field, date_slice=test_date_slice)
            , self.config).read_records(sync_mode=None)
        
        # checking iteratively if the job is completed, then return the URL with jsonl datafile
        job_data_url = ZuoraJobStatusCheck(list(job_id)[0], self.config).read_records(sync_mode=None)
        
        # read records from completed subtmited job
        job_result = ZuoraGetJobResult(list(job_data_url)[0], self.config).read_records(sync_mode=None)
        
        # Return True if we have successfully read records from completed job
        assert len(list(job_result)) > 0