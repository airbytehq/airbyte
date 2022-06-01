#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.sources.declarative.extractors.jq import JqExtractor
from airbyte_cdk.sources.declarative.response import Response

config = {"field": "record_array"}


def test():
    transform = ".data[]"
    extractor = JqExtractor(transform, config)

    records = [{"id": 1}, {"id": 2}]
    body = {"data": records}
    response = create_response(body)
    actual_records = extractor.extract_records(response)

    assert actual_records == records


def test_field_in_config():
    transform = ".{{ config['field'] }}[]"
    extractor = JqExtractor(transform, config)

    records = [{"id": 1}, {"id": 2}]
    body = {"record_array": records}
    response = create_response(body)
    actual_records = extractor.extract_records(response)

    assert actual_records == records


def test_field_in_kwargs():
    transform = ".{{ kwargs['data_field'] }}[]"
    kwargs = {"data_field": "records"}
    extractor = JqExtractor(transform, config, kwargs=kwargs)

    records = [{"id": 1}, {"id": 2}]
    body = {"records": records}
    response = create_response(body)
    actual_records = extractor.extract_records(response)

    assert actual_records == records


def create_response(body):
    return Response(body=body)


def test_default():
    transform = ".{{kwargs['field']}}[]"
    extractor = JqExtractor(transform, config)

    records = [{"id": 1}, {"id": 2}]
    response = create_response(records)
    actual_records = extractor.extract_records(response)

    assert actual_records == records


def test_extract_an_object():
    transform = "."
    extractor = JqExtractor(transform, config)

    records = [{"id": 1}, {"id": 2}]
    body = {"records": records}
    response = create_response(body)
    actual_records = extractor.extract_records(response)

    assert actual_records == body
