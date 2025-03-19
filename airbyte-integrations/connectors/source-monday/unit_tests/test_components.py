#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from typing import Any

from requests import Response
from source_monday.extractor import MondayIncrementalItemsExtractor


def _create_response(content: Any) -> Response:
    response = Response()
    response._content = json.dumps(content).encode("utf-8")
    return response


def test_null_records(caplog):
    extractor = MondayIncrementalItemsExtractor(
        field_path=["data", "boards", "*"],
        config={},
        parameters={},
    )
    content = {
        "data": {
            "boards": [
                {"board_kind": "private", "id": "1234561", "updated_at": "2023-08-15T10:30:49Z"},
                {"board_kind": "private", "id": "1234562", "updated_at": "2023-08-15T10:30:50Z"},
                {"board_kind": "private", "id": "1234563", "updated_at": "2023-08-15T10:30:51Z"},
                {"board_kind": "private", "id": "1234564", "updated_at": "2023-08-15T10:30:52Z"},
                {"board_kind": "private", "id": "1234565", "updated_at": "2023-08-15T10:30:43Z"},
                {"board_kind": "private", "id": "1234566", "updated_at": "2023-08-15T10:30:54Z"},
                None,
                None,
            ]
        },
        "errors": [{"message": "Cannot return null for non-nullable field Board.creator"}],
        "account_id": 123456,
    }
    response = _create_response(content)
    records = list(extractor.extract_records(response))
    warning_message = "Record with null value received; errors: [{'message': 'Cannot return null for non-nullable field Board.creator'}]"
    assert warning_message in caplog.messages
    expected_records = [
        {"board_kind": "private", "id": "1234561", "updated_at": "2023-08-15T10:30:49Z", "updated_at_int": 1692095449},
        {"board_kind": "private", "id": "1234562", "updated_at": "2023-08-15T10:30:50Z", "updated_at_int": 1692095450},
        {"board_kind": "private", "id": "1234563", "updated_at": "2023-08-15T10:30:51Z", "updated_at_int": 1692095451},
        {"board_kind": "private", "id": "1234564", "updated_at": "2023-08-15T10:30:52Z", "updated_at_int": 1692095452},
        {"board_kind": "private", "id": "1234565", "updated_at": "2023-08-15T10:30:43Z", "updated_at_int": 1692095443},
        {"board_kind": "private", "id": "1234566", "updated_at": "2023-08-15T10:30:54Z", "updated_at_int": 1692095454},
    ]
    assert records == expected_records
