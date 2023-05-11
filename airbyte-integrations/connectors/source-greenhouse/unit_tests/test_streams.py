#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json

import pytest
import requests
from source_greenhouse.source import SourceGreenhouse


@pytest.fixture
def applications_stream():
    source = SourceGreenhouse()
    streams = source.streams({})

    return [s for s in streams if s.name == "applications"][0]


def create_response(headers):
    response = requests.Response()
    response_body = {"next": "https://airbyte.io/next_url"}
    response._content = json.dumps(response_body).encode("utf-8")
    response.headers = headers
    return response


def test_next_page_token_has_next(applications_stream):
    headers = {"link": '<https://harvest.greenhouse.io/v1/applications?per_page=100&since_id=123456789>; rel="next"'}
    response = create_response(headers)
    next_page_token = applications_stream.retriever.next_page_token(response=response)
    assert next_page_token == {"next_page_token": "https://harvest.greenhouse.io/v1/applications?per_page=100&since_id=123456789"}


def test_next_page_token_has_not_next(applications_stream):
    response = create_response({})
    next_page_token = applications_stream.retriever.next_page_token(response=response)

    assert next_page_token is None


def test_request_params_next_page_token_is_not_none(applications_stream):
    response = create_response({"link": f'<https://harvest.greenhouse.io/v1/applications?per_page={100}&since_id=123456789>; rel="next"'})
    next_page_token = applications_stream.retriever.next_page_token(response=response)
    request_params = applications_stream.retriever.request_params(next_page_token=next_page_token, stream_state={})
    path = applications_stream.retriever.path(next_page_token=next_page_token, stream_state={})
    assert "applications?per_page=100&since_id=123456789" == path
    assert request_params == {"per_page": 100}


def test_request_params_next_page_token_is_none(applications_stream):
    request_params = applications_stream.retriever.request_params(stream_state={})

    assert request_params == {"per_page": 100}


def test_parse_response_expected_response(applications_stream):
    response = requests.Response()
    response.status_code = 200
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
    parsed_response = applications_stream.retriever.parse_response(response, stream_state={})
    records = [record for record in parsed_response]

    assert records == json.loads(response_content)


def test_parse_response_empty_content(applications_stream):
    response = requests.Response()
    response.status_code = 200
    response._content = b"[]"
    parsed_response = applications_stream.retriever.parse_response(response, stream_state={})
    records = [record for record in parsed_response]

    assert records == []


def test_number_of_streams():
    source = SourceGreenhouse()
    streams = source.streams({})
    assert len(streams) == 36


def test_ignore_403(applications_stream):
    response = requests.Response()
    response.status_code = 403
    response._content = b""
    parsed_response = applications_stream.retriever.parse_response(response, stream_state={})
    records = [record for record in parsed_response]
    assert records == []


def test_retry_429(applications_stream):
    response = requests.Response()
    response.status_code = 429
    response._content = b"{}"
    should_retry = applications_stream.retriever.should_retry(response)
    assert should_retry is True
