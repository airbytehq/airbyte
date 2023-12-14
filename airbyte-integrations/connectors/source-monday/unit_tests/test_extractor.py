#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_monday.extractor import MondayActivityExtractor


def test_extract_records():
    # Mock the response
    response = MagicMock()
    response_body = {
        "data": {
            "boards": [
                {
                    "activity_logs": [
                        {
                            "data": "{\"pulse_id\": 123}",
                            "entity": "pulse",
                            "created_at": "16367386880000000"
                        }
                    ]
                }
            ]
        }
    }

    response.json.return_value = response_body
    extractor = MondayActivityExtractor(parameters={})
    records = extractor.extract_records(response)

    # Assertions
    assert len(records) == 1
    assert records[0]["pulse_id"] == 123
    assert records[0]["created_at_int"] == 1636738688
