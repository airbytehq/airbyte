#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import json

import pytest
import requests
from source_pipedrive.extractor import NullCheckedDpathExtractor


@pytest.mark.parametrize(
    "response_body, expected_records",
    [
        pytest.param(
            {"data": [{"id": 1, "data": None}, {"id": 2, "data": None}]},
            [{"id": 1, "data": None}, {"id": 2, "data": None}],
            id="test_with_null_nested_field",
        ),
        pytest.param(
            {"data": [{"id": 1, "data": {"id": 1, "user_id": "123"}}, {"id": 2, "data": {"id": 2, "user_id": "123"}}]},
            [{"id": 1, "user_id": "123"}, {"id": 2, "user_id": "123"}],
            id="test_with_nested_field",
        ),
    ],
)
def test_pipedrive_extractor(response_body, expected_records):
    extractor = NullCheckedDpathExtractor(field_path=["data", "*"], nullable_nested_field="data", config={}, parameters={})
    response = _create_response(response_body)
    records = extractor.extract_records(response)

    assert records == expected_records


def _create_response(body):
    response = requests.Response()
    response._content = json.dumps(body).encode("utf-8")
    return response
