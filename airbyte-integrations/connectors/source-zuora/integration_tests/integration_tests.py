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
from datetime import timedelta
from typing import Any, Dict, Mapping

import pendulum
from source_zuora.zuora_auth import ZuoraAuthenticator
from source_zuora.zuora_client import ZoqlExportClient


def _config() -> Mapping[str, Any]:
    """ 
    Get the config from /test_input
    """
    with open("secrets/config.json", "r") as f:
        return json.loads(f.read())


class TestClient:
    """ 
    Make instance of the ZoqlExportClient using input config.json
    """
    def client(config: Dict = _config()):
        auth_client = ZuoraAuthenticator(config["is_sandbox"])
        authenticator = auth_client.generateToken(config["client_id"], config["client_secret"]).get("header")
        zuora_client = ZoqlExportClient(authenticator=authenticator, url_base=auth_client.endpoint, **config)
        return zuora_client



# Output example from ZoqlExportClient.zuora_get_json_schema
zuora_schema = [
    {"field": "field_1", "type": "date"},
    {"field": "field_2", "type": "varchar"},
    {"field": "field_3", "type": "decimal(22,9)"},
    {"field": "field_4", "type": "timestamp with time zone"},
    {"field": "field_5", "type": "integer"},
    {"field": "field_6", "type": "bigint"},
    {"field": "field_7", "type": "zoql"},
    {"field": "field_8", "type": "xml"},
    {"field": "field_9", "type": "blob"},
    {"field": "field_10", "type": "array"},
    {"field": "field_11", "type": "list"},
]

# Output expected from ZoqlExportClient.convert_schema_types
json_schema = {
    "field_1": {"type": ["string", "null"]},
    "field_2": {"type": ["string", "null"]},
    "field_3": {"type": ["number", "null"]},
    "field_4": {"type": ["string", "null"]},
    "field_5": {"type": ["number", "null"]},
    "field_6": {"type": ["number", "null"]},
    "field_7": {"type": ["object", "null"]},
    "field_8": {"type": ["object", "null"]},
    "field_9": {"type": ["object", "null"]},
    "field_10": {"type": ["array", "null"]},
    "field_11": {"type": ["array", "null"]},
}

# Define Test stream, test_date_field (cursor_field), test_field for check
test_stream = "account"
test_date_field = "updateddate"
test_field = "id"


def test_convert_to_schema():
    """
    Test some popular Zuora Data Types to be converted to JSONSchema types.
    """
    converted_schema = TestClient.client().convert_schema_types(schema=zuora_schema)
    assert converted_schema == json_schema


def test_zuora_list_streams():
    """
    Test getting list of Zuora objects (streams) from account
    :: the ACCOUNT object is standard so it should be defenetly in the output
    """
    zuora_streams_list = TestClient.client().zuora_list_streams()
    assert True if test_stream in zuora_streams_list else False


def test_zuora_get_json_schema():
    """
    Test getting JSONSchema for STREAM
    """
    expect_test_field_json_schema_type = {"type": ["string", "null"]}
    json_schema = TestClient.client().zuora_get_json_schema(test_stream)
    assert True if json_schema.get(test_field) == expect_test_field_json_schema_type else False


def test_to_datetime_str():
    """
    Test of correct conversion from datetime object to formated datetime string
    The output from this method should be formated as follows:
    :: "YYYY-mm-dd HH:mm:ss Z" or "%Y-%m-%d %H:%M:%S %Z"
    :: example: '2021-07-15 07:45:55 -07:00'
    """
    input_datetime = pendulum.now().astimezone()
    formated_datetime_str = input_datetime.strftime("%Y-%m-%d %H:%M:%S %Z")
    converted_datetime_str = TestClient.client().to_datetime_str(input_datetime)
    assert converted_datetime_str == formated_datetime_str


def test_make_query_select():

    """
    Test to check make_query method works correctly, building the 'select' statement for outgoing data job
    """

    test_start_date = TestClient.client().to_datetime_str(pendulum.yesterday().astimezone())
    test_end_date = TestClient.client().to_datetime_str(pendulum.today().astimezone())

    test_args = {
        "q_type": "select",
        "obj": test_stream,
        "date_field": test_date_field,
        "start_date": test_start_date,
        "end_date": test_end_date,
    }
    test_expected_query_output = {
        "compression": "NONE",
        "output": {"target": "S3"},
        "outputFormat": "JSON",
        "query": f"select * from {test_stream} where {test_date_field} >= TIMESTAMP '{test_start_date}' and {test_date_field} <= TIMESTAMP '{test_end_date}'",
    }

    test_query = TestClient.client().make_query(**test_args)
    assert test_query == test_expected_query_output


def test_get_data_with_date_slice():
    """
    Test to get data from the ACCOUNT stream

    :: ! IF THIS TEST IS FAILING DURING THE BULD STAGE, CHECK THE 'start_date' input argument !

        :: ' test_args ' is the representation of arguments that must be supplied as input

        We iterate over the generator object, so the list() function is used as placeholder in this test
        With this test we are testing the set of methods working together as far as ' get_data_with_date_slice() '
        is a wraper for the following methods:

        ::  ' get_data() ', ' submit_job() ', ' check_job_status() ', ' get_job_data() '

    :: ! IF THIS TEST IS FAILING DURING THE BULD STAGE, CHECK THE 'start_date' input argument !
    """

    test_args = {
        "q_type": "select",
        "obj": test_stream,
        "date_field": test_date_field,
        "start_date": (pendulum.now() - timedelta(days=364)).to_date_string(),
        "window_days": 300,
    }

    test_data = list(TestClient.client().get_data_with_date_slice(**test_args))
    assert True if len(test_data) > 0 else False


