#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import requests
from airbyte_cdk.models import SyncMode
from pytest import fixture
#from source_onesignal.streams import Apps, Devices, IncrementalOnesignalStream, Notifications

#from source_hydrovu.source import HydroVuStream
#from source_hydrovu.source import IncrementalHydrovuStream
from source_hydrovu.source import Locations
from source_hydrovu.source import Readings


# NOTE: Look to One Signal connector for example unit tests on incremental streams


@fixture
def config():
    return {"config": {"token_refresh_endpoint": "https://www.hydrovu.com/public-api/oauth/token", "client_id": "ABC", "client_secret": "secret", }}


def test_locations_next_page_token(requests_mock):
    stream = Locations()

    requests_mock.get("https://dummy")
    resp = requests.get("https://dummy")
    expected_next_page_token = None
    assert stream.next_page_token(resp) == expected_next_page_token

    requests_mock.get("https://dummy", headers={"X-ISI-Next-Page": "aaa111"})
    resp = requests.get("https://dummy")
    expected_next_page_token = "aaa111"
    assert stream.next_page_token(resp) == expected_next_page_token


def test_locations_request_headers():
     
    stream = Locations()
    inputs = {"stream_state": "", "next_page_token": "aaa111"}
    expected_request_headers = {"X-ISI-Start-Page": "aaa111"}

    assert stream.request_headers(**inputs) == expected_request_headers


def test_locations_parse_response(requests_mock):
     
    stream = Locations()

    requests_mock.get("https://dummy", json=[{
        "id": 1234,
        "name": "Well-1",
        "description": "5555",
        "gps": {
            "latitude": 34.5678,
            "longitude": -123.456
         }
    }])

    resp = requests.get("https://dummy")

    expected_parsed_response = {
        "id": 1234,
        "name": "Well-1",
        "description": "5555",
        "latitude": 34.5678,
        "longitude": -123.456
    }

    parsed_response = {}

    parsed_response_generator = stream.parse_response(resp)

    for record in list(parsed_response_generator):
        for key, value in record.items():
            parsed_response[str(key)] = value

    assert parsed_response == expected_parsed_response


# The rest of the unit tests are scaffolded to be completed in the future

def test_readings_request_headers():
    
    auth = "bbbb"

    #stream = Readings(auth)
    inputs = {"stream_state": "", "next_page_token": "aaa111"}
    expected_request_headers = {"X-ISI-Start-Page": "aaa111"}

    #assert stream.request_headers(**inputs) == expected_request_headers

    assert True


def test_readings_request_params():

    assert True


def test_readings_next_page_token():

    assert True


def test_readings_state_property():

    assert True


def test_readings_state_setter():
    
    assert True


def test_readings_parse_response():

    assert True


def test_parameters_request_headers():

    assert True


def test_parameters_next_page_token():

    assert True


def test_parameters_parse_response():

    assert True


def test_units_request_headers():

    assert True


def test_units_next_page_token():

    assert True


def test_units_parse_response():

    assert True

