#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import io
import json
import logging
from unittest.mock import Mock

import pytest
from source_file.source import SourceFile

json_obj = {
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


json_array = [
    {
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
    },
    {
        "id": "0002",
        "type": "donut",
        "name": "Raised",
        "ppu": 0.55,
        "batters": {"batter": [{"id": "1001", "type": "Regular"}]},
        "topping": [
            {"id": "5001", "type": "None"},
            {"id": "5002", "type": "Glazed"},
            {"id": "5005", "type": "Sugar"},
            {"id": "5003", "type": "Chocolate"},
            {"id": "5004", "type": "Maple"},
        ],
    },
    {
        "id": "0003",
        "type": "donut",
        "name": "Old Fashioned",
        "ppu": 0.55,
        "batters": {"batter": [{"id": "1001", "type": "Regular"}, {"id": "1002", "type": "Chocolate"}]},
        "topping": [
            {"id": "5001", "type": "None"},
            {"id": "5002", "type": "Glazed"},
            {"id": "5003", "type": "Chocolate"},
            {"id": "5004", "type": "Maple"},
        ],
    },
]


expected_obj_schema = {
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
    "required": ["batters", "id", "name", "ppu", "topping", "type"],
    "type": "object",
}


expected_array_schema = {
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
            "items": {
                "properties": {"id": {"type": "string"}, "type": {"type": "string"}},
                "required": ["id", "type"],
                "type": "object",
            },
            "type": "array",
        },
        "type": {"type": "string"},
    },
    "required": ["batters", "id", "name", "ppu", "topping", "type"],
    "type": "object",
}


@pytest.mark.parametrize("input_json, expected_schema", ((json_obj, expected_obj_schema), (json_array, expected_array_schema)))
def test_json_schema(mocker, config, input_json, expected_schema):
    source = SourceFile()
    mocker.patch("source_file.client.URLFile._open", Mock(return_value=io.StringIO(json.dumps(input_json))))
    catalog = source.discover(logger=logging.getLogger("airbyte"), config=config)
    assert len(catalog.streams) == 1
    stream = next(iter(catalog.streams))
    assert stream.json_schema == expected_schema
