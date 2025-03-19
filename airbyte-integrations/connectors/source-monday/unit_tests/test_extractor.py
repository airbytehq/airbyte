#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from unittest.mock import MagicMock

from source_monday.extractor import MondayActivityExtractor, MondayIncrementalItemsExtractor


def test_extract_records():
    # Mock the response
    response = MagicMock()
    response_body = {
        "data": {"boards": [{"activity_logs": [{"data": '{"pulse_id": 123}', "entity": "pulse", "created_at": "16367386880000000"}]}]}
    }

    response.content = json.dumps(response_body).encode("utf-8")

    extractor = MondayActivityExtractor(parameters={})
    records = list(extractor.extract_records(response))

    # Assertions
    assert len(records) == 1
    assert records[0]["pulse_id"] == 123
    assert records[0]["created_at_int"] == 1636738688


def test_empty_activity_logs_extract_records():
    response = MagicMock()
    response_body = {"data": {"boards": [{"activity_logs": None}]}}

    response.content = json.dumps(response_body).encode("utf-8")
    extractor = MondayActivityExtractor(parameters={})
    records = list(extractor.extract_records(response))

    assert len(records) == 0


def test_extract_records_incremental():
    # Mock the response
    response = MagicMock()
    response_body = {"data": {"boards": [{"id": 1, "column_values": [{"id": 11, "text": None, "display_value": "Hola amigo!"}]}]}}

    response.content = json.dumps(response_body).encode("utf-8")
    extractor = MondayIncrementalItemsExtractor(
        parameters={},
        field_path=["data", "ccccc"],
        config=MagicMock(),
        field_path_pagination=["data", "bbbb"],
        field_path_incremental=["data", "boards", "*"],
    )
    records = list(extractor.extract_records(response))

    # Assertions
    assert records == [{"id": 1, "column_values": [{"id": 11, "text": "Hola amigo!", "display_value": "Hola amigo!"}]}]
