# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from dataclasses import dataclass
from typing import Any, Mapping
from unittest.mock import Mock

import pytest
from source_us_census.components import USCensusSchema


@dataclass
class MockConfig:
    query_params: str = None

    def get(self, key):
        if key == "query_params":
            return self.query_params


@pytest.fixture
def census_schema():
    def _create_schema(query_params=None):
        config = MockConfig(query_params=query_params)
        return USCensusSchema(config=config)
    return _create_schema


def test_get_json_schema_basic_case(census_schema):
    schema_instance = census_schema(query_params="get=NAME,POP&for=state:*")
    schema = schema_instance.get_json_schema()

    expected_properties = {
        "NAME": {"type": "string"},
        "POP": {"type": "string"},
        "state": {"type": "string"}
    }

    assert schema["properties"] == expected_properties
    assert schema["$schema"] == "http://json-schema.org/draft-07/schema#"
    assert schema["type"] == "object"
    assert schema["additionalProperties"] is True


def test_get_json_schema_with_get_param(census_schema):
    schema_instance = census_schema(query_params="get=NAME,AGE,EMPLOYMENT")
    schema = schema_instance.get_json_schema()

    expected_properties = {
        "NAME": {"type": "string"},
        "AGE": {"type": "string"},
        "EMPLOYMENT": {"type": "string"}
    }

    assert schema["properties"] == expected_properties


def test_get_json_schema_with_for_param(census_schema):
    schema_instance = census_schema(query_params="for=county:1234")
    schema = schema_instance.get_json_schema()

    expected_properties = {
        "county": {"type": "string"}
    }

    assert schema["properties"] == expected_properties


def test_get_json_schema_with_additional_params(census_schema):
    schema_instance = census_schema(query_params="get=NAME&year=2020&for=us:*")
    schema = schema_instance.get_json_schema()

    expected_properties = {
        "NAME": {"type": "string"},
        "year": {"type": "string"},
        "us": {"type": "string"}
    }

    assert schema["properties"] == expected_properties


def test_get_json_schema_no_query_params(census_schema):
    schema_instance = census_schema(query_params=None)
    schema = schema_instance.get_json_schema()

    expected_properties = {
        "{  @context: https://project-open-data.cio.gov/v1.1/schema/catalog.jsonld": {"type": "string"}
    }

    assert schema["properties"] == expected_properties
