#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from unittest.mock import Mock, call

import pytest
import requests
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.extractors.dpath_extractor import DpathExtractor
from airbyte_cdk.sources.declarative.extractors.record_filter import RecordFilter
from airbyte_cdk.sources.declarative.extractors.record_selector import RecordSelector
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.types import Record
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer


@pytest.mark.parametrize(
    "test_name, field_path, filter_template, body, expected_data",
    [
        (
            "test_with_extractor_and_filter",
            ["data"],
            "{{ record['created_at'] > stream_state['created_at'] }}",
            {"data": [{"id": 1, "created_at": "06-06-21"}, {"id": 2, "created_at": "06-07-21"}, {"id": 3, "created_at": "06-08-21"}]},
            [{"id": 2, "created_at": "06-07-21"}, {"id": 3, "created_at": "06-08-21"}],
        ),
        (
            "test_no_record_filter_returns_all_records",
            ["data"],
            None,
            {"data": [{"id": 1, "created_at": "06-06-21"}, {"id": 2, "created_at": "06-07-21"}]},
            [{"id": 1, "created_at": "06-06-21"}, {"id": 2, "created_at": "06-07-21"}],
        ),
        (
            "test_with_extractor_and_filter_with_parameters",
            ["{{ parameters['parameters_field'] }}"],
            "{{ record['created_at'] > parameters['created_at'] }}",
            {"data": [{"id": 1, "created_at": "06-06-21"}, {"id": 2, "created_at": "06-07-21"}, {"id": 3, "created_at": "06-08-21"}]},
            [{"id": 3, "created_at": "06-08-21"}],
        ),
        (
            "test_read_single_record",
            ["data"],
            None,
            {"data": {"id": 1, "created_at": "06-06-21"}},
            [{"id": 1, "created_at": "06-06-21"}],
        ),
        (
            "test_no_record",
            ["data"],
            None,
            {"data": []},
            [],
        ),
        (
            "test_no_record_from_root",
            [],
            None,
            [],
            [],
        ),
    ],
)
def test_record_filter(test_name, field_path, filter_template, body, expected_data):
    config = {"response_override": "stop_if_you_see_me"}
    parameters = {"parameters_field": "data", "created_at": "06-07-21"}
    stream_state = {"created_at": "06-06-21"}
    stream_slice = {"last_seen": "06-10-21"}
    next_page_token = {"last_seen_id": 14}
    schema = create_schema()
    first_transformation = Mock(spec=RecordTransformation)
    second_transformation = Mock(spec=RecordTransformation)
    transformations = [first_transformation, second_transformation]

    response = create_response(body)
    decoder = JsonDecoder(parameters={})
    extractor = DpathExtractor(field_path=field_path, decoder=decoder, config=config, parameters=parameters)
    if filter_template is None:
        record_filter = None
    else:
        record_filter = RecordFilter(config=config, condition=filter_template, parameters=parameters)
    record_selector = RecordSelector(
        extractor=extractor,
        record_filter=record_filter,
        transformations=transformations,
        config=config,
        parameters=parameters,
        schema_normalization=TypeTransformer(TransformConfig.NoTransform),
    )

    actual_records = list(
        record_selector.select_records(
            response=response, records_schema=schema, stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token
        )
    )
    assert actual_records == [Record(data, stream_slice) for data in expected_data]

    calls = []
    for record in expected_data:
        calls.append(call(record, config=config, stream_state=stream_state, stream_slice=stream_slice))
    for transformation in transformations:
        assert transformation.transform.call_count == len(expected_data)
        transformation.transform.assert_has_calls(calls)


@pytest.mark.parametrize(
    "test_name, schema, schema_transformation, body, expected_data",
    [
        (
            "test_with_empty_schema",
            {},
            TransformConfig.NoTransform,
            {"data": [{"id": 1, "created_at": "06-06-21", "field_int": "100", "field_float": "123.3"}]},
            [{"id": 1, "created_at": "06-06-21", "field_int": "100", "field_float": "123.3"}],
        ),
        (
            "test_with_schema_none_normalizer",
            {},
            TransformConfig.NoTransform,
            {"data": [{"id": 1, "created_at": "06-06-21", "field_int": "100", "field_float": "123.3"}]},
            [{"id": 1, "created_at": "06-06-21", "field_int": "100", "field_float": "123.3"}],
        ),
        (
            "test_with_schema_and_default_normalizer",
            {},
            TransformConfig.DefaultSchemaNormalization,
            {"data": [{"id": 1, "created_at": "06-06-21", "field_int": "100", "field_float": "123.3"}]},
            [{"id": "1", "created_at": "06-06-21", "field_int": 100, "field_float": 123.3}],
        ),
    ],
)
def test_schema_normalization(test_name, schema, schema_transformation, body, expected_data):
    config = {"response_override": "stop_if_you_see_me"}
    parameters = {"parameters_field": "data", "created_at": "06-07-21"}
    stream_state = {"created_at": "06-06-21"}
    stream_slice = {"last_seen": "06-10-21"}
    next_page_token = {"last_seen_id": 14}

    response = create_response(body)
    schema = create_schema()
    decoder = JsonDecoder(parameters={})
    extractor = DpathExtractor(field_path=["data"], decoder=decoder, config=config, parameters=parameters)
    record_selector = RecordSelector(
        extractor=extractor,
        record_filter=None,
        transformations=[],
        config=config,
        parameters=parameters,
        schema_normalization=TypeTransformer(schema_transformation),
    )

    actual_records = list(
        record_selector.select_records(
            response=response,
            stream_state=stream_state,
            stream_slice=stream_slice,
            next_page_token=next_page_token,
            records_schema=schema,
        )
    )

    assert actual_records == [Record(data, stream_slice) for data in expected_data]


def create_response(body):
    response = requests.Response()
    response._content = json.dumps(body).encode("utf-8")
    return response


def create_schema():
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "created_at": {"type": "string"},
            "field_int": {"type": "integer"},
            "field_float": {"type": "number"},
        },
    }
