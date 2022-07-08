#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import io
import json
import logging
from unittest.mock import Mock

from source_file.source import SourceFile

input_json = {
    "id": "0001",
    "type": "donut",
    "name": "Cake",
    "ppu": 0.55,
    "batters": {
        "batter": [
            {"id": "1001", "type": "Regular"},
            {"id": "1002", "type": "Chocolate"},
            {"id": "1003", "type": "Blueberry"},
            {"id": "1004", "type": "Devil's Food"},
        ]
    },
    "topping": [
        {"id": "5001", "type": "None"},
        {"id": "5002", "type": "Glazed"},
        {"id": "5005", "type": "Sugar"},
        {"id": "5007", "type": "Powdered Sugar"},
        {"id": "5006", "type": "Chocolate with Sprinkles"},
        {"id": "5003", "type": "Chocolate"},
        {"id": "5004", "type": "Maple"},
    ],
}


expected_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "properties": {
        "batters": {
            "properties": {
                "batter": {
                    "items": {
                        "properties": {"id": {"type": "string"}, "type": {"type": "string"}},
                        "required": ["id", "type"],
                        "type": "object",
                    },
                    "type": "array",
                }
            },
            "required": ["batter"],
            "type": "object",
        },
        "id": {"type": "string"},
        "name": {"type": "string"},
        "ppu": {"type": "number"},
        "topping": {
            "items": {"properties": {"id": {"type": "string"}, "type": {"type": "string"}}, "required": ["id", "type"], "type": "object"},
            "type": "array",
        },
        "type": {"type": "string"},
    },
    "type": "object",
}


def test_json_schema(mocker, config):
    source = SourceFile()
    mocker.patch("source_file.client.URLFile._open", Mock(return_value=io.StringIO(json.dumps(input_json))))
    catalog = source.discover(logger=logging.getLogger("airbyte"), config=config)
    assert len(catalog.streams) == 1
    stream = next(iter(catalog.streams))
    assert stream.json_schema == expected_schema
