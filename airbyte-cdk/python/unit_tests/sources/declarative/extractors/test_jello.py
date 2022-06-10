#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json

import requests
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.extractors.jello import JelloExtractor

config = {"field": "record_array"}
decoder = JsonDecoder()


def test():
    transform = "_.data"
    extractor = JelloExtractor(transform, decoder, config)

    records = [{"id": 1}, {"id": 2}]
    body = {"data": records}
    response = create_response(body)
    actual_records = extractor.extract_records(response)

    assert actual_records == records


def test_field_in_config():
    transform = "_.{{ config['field'] }}"
    extractor = JelloExtractor(transform, decoder, config)

    records = [{"id": 1}, {"id": 2}]
    body = {"record_array": records}
    response = create_response(body)
    actual_records = extractor.extract_records(response)

    assert actual_records == records


def test_field_in_kwargs():
    transform = "_.{{ kwargs['data_field'] }}"
    kwargs = {"data_field": "records"}
    extractor = JelloExtractor(transform, decoder, config, kwargs=kwargs)

    records = [{"id": 1}, {"id": 2}]
    body = {"records": records}
    response = create_response(body)
    actual_records = extractor.extract_records(response)

    assert actual_records == records


def create_response(body):
    response = requests.Response()
    response._content = json.dumps(body).encode("utf-8")
    return response


def test_default():
    transform = "_{{kwargs['field']}}"
    extractor = JelloExtractor(transform, decoder, config)

    records = [{"id": 1}, {"id": 2}]
    response = create_response(records)
    actual_records = extractor.extract_records(response)

    assert actual_records == records
