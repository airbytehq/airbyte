#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json

import requests
from source_qualaroo.components import CustomAuthenticator, CustomExtractor


def test_token_generation():

    config = {"key": "4524324", "token": "token"}
    authenticator = CustomAuthenticator(config=config, username="example@gmail.com", password="api_key", parameters=None)
    token = authenticator.token
    expected_token = "Basic ZXhhbXBsZUBnbWFpbC5jb206YXBpX2tleQ=="
    assert expected_token == token


def test_extract_records_with_answered_questions():

    response_data = [
        {"id": 1, "answered_questions": {"q1": "A1", "q2": "A2"}},
        {"id": 2, "answered_questions": {"q3": "A3"}},
    ]
    response = requests.Response()
    response._content = json.dumps(response_data).encode("utf-8")
    extracted_records = CustomExtractor().extract_records(response)
    expected_records = [{"id": 1, "answered_questions": ["A1", "A2"]}, {"id": 2, "answered_questions": ["A3"]}]
    assert expected_records == extracted_records
