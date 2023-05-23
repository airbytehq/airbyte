#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
import requests
from source_freshservice.streams import FreshserviceStream, Tickets


@pytest.fixture
def patch_base_class(mocker):
    mocker.patch.object(FreshserviceStream, "path", "v0/example_endpoint")
    # mocker.patch.object(FreshserviceStream, "domain_name", "https://example.example")


def test_request_params(patch_base_class):
    stream = FreshserviceStream()
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {"per_page": 30}
    assert stream.request_params(**inputs) == expected_params


class Fake(object):
    pass


def test_next_page_token(patch_base_class):
    stream = FreshserviceStream()
    response = Fake()
    response.links = {'next': {'url': 'https://dummy?page=3'}}
    inputs = {'response': response}
    expected_token = {'page': '3'}
    assert stream.next_page_token(**inputs) == expected_token


def test_next_page_token_when_no_next_page(patch_base_class):
    stream = FreshserviceStream()
    response = Fake()
    response.links = {}
    inputs = {'response': response}
    assert stream.next_page_token(**inputs) is None


def test_parse_response(patch_base_class, requests_mock):
    stream = Tickets()
    requests_mock.get('https://dummy', json={
        "tickets": [
            {
                "subject": "test",
                "group_id": 18000074057
            }
        ]
    })
    res = requests.get('https://dummy')
    inputs = {'response': res}
    expected_parsed = {"subject": "test", "group_id": 18000074057}
    assert next(stream.parse_response(**inputs)) == expected_parsed
