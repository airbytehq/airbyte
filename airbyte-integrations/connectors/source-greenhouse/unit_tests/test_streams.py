#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
from json import JSONDecodeError
from types import GeneratorType

import pytest
import requests
from requests.auth import HTTPBasicAuth
from source_greenhouse.streams import Applications


@pytest.fixture
def applications_stream():
    auth = HTTPBasicAuth("api_key", "")
    stream = Applications(authenticator=auth)
    return stream


def test_next_page_token_has_next(applications_stream):
    response = requests.Response()
    response.headers = {
        "link": f'<https://harvest.greenhouse.io/v1/applications?per_page={Applications.page_size}&since_id=123456789>; rel="next"'
    }
    next_page_token = applications_stream.next_page_token(response=response)
    assert next_page_token == {"per_page": str(Applications.page_size), "since_id": "123456789"}


def test_next_page_token_has_not_next(applications_stream):
    response = requests.Response()
    next_page_token = applications_stream.next_page_token(response=response)

    assert next_page_token == {}


def test_request_params_next_page_token_is_not_none(applications_stream):
    response = requests.Response()
    response.headers = {
        "link": f'<https://harvest.greenhouse.io/v1/applications?per_page={Applications.page_size}&since_id=123456789>; rel="next"'
    }
    next_page_token = applications_stream.next_page_token(response=response)
    request_params = applications_stream.request_params(next_page_token=next_page_token, stream_state={})

    assert request_params == {"per_page": str(Applications.page_size), "since_id": "123456789"}


def test_request_params_next_page_token_is_none(applications_stream):
    request_params = applications_stream.request_params(stream_state={})

    assert request_params == {"per_page": Applications.page_size}


def test_parse_response_expected_response(applications_stream):
    response = requests.Response()
    response_content = b"""
        [
          {
            "status": "active",
            "source": {
              "public_name": "HRMARKET",
              "id": 4000067003
            },
            "rejection_reason": null,
            "rejection_details": null,
            "rejected_at": null,
            "prospective_office": null,
            "prospective_department": null,
            "prospect_detail": {
              "prospect_stage": null,
              "prospect_pool": null,
              "prospect_owner": {
                "name": "John Lafleur",
                "id": 4218086003
              }
            },
            "prospect": true,
            "location": null,
            "last_activity_at": "2020-11-24T23:24:37.049Z",
            "jobs": [],
            "job_post_id": null,
            "id": 19214950003,
            "current_stage": null,
            "credited_to": {
              "name": "John Lafleur",
              "last_name": "Lafleur",
              "id": 4218086003,
              "first_name": "John",
              "employee_id": null
            },
            "candidate_id": 17130511003,
            "attachments": [],
            "applied_at": "2020-11-24T23:24:37.023Z",
            "answers": []
          },
          {
            "status": "active",
            "source": {
              "public_name": "Jobs page on your website",
              "id": 4000177003
            },
            "rejection_reason": null,
            "rejection_details": null,
            "rejected_at": null,
            "prospective_office": null,
            "prospective_department": null,
            "prospect_detail": {
              "prospect_stage": null,
              "prospect_pool": null,
              "prospect_owner": {
                "name": "John Lafleur",
                "id": 4218086003
              }
            },
            "prospect": true,
            "location": null,
            "last_activity_at": "2020-11-24T23:25:13.804Z",
            "jobs": [],
            "job_post_id": null,
            "id": 19214993003,
            "current_stage": null,
            "credited_to": {
              "name": "John Lafleur",
              "last_name": "Lafleur",
              "id": 4218086003,
              "first_name": "John",
              "employee_id": null
            },
            "candidate_id": 17130554003,
            "attachments": [],
            "applied_at": "2020-11-24T23:25:13.781Z",
            "answers": []
          }
        ]
    """
    response._content = response_content
    parsed_response = applications_stream.parse_response(response)
    records = [record for record in parsed_response]

    assert isinstance(parsed_response, GeneratorType)
    assert records == json.loads(response_content)


def test_parse_response_empty_content(applications_stream):
    response = requests.Response()
    response._content = b"[]"
    parsed_response = applications_stream.parse_response(response)
    records = [record for record in parsed_response]

    assert isinstance(parsed_response, GeneratorType)
    assert records == []


def test_parse_response_invalid_content(applications_stream):
    response = requests.Response()
    response._content = b"not json"
    parsed_response = applications_stream.parse_response(response)

    assert isinstance(parsed_response, GeneratorType)
    with pytest.raises(JSONDecodeError):
        for _ in parsed_response:
            pass
