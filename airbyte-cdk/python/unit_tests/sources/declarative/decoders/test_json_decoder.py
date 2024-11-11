#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import gzip
import json
import os

import pytest
import requests
from airbyte_cdk import YamlDeclarativeSource
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder, JsonlDecoder
from airbyte_cdk.sources.declarative.models import DeclarativeStream as DeclarativeStreamModel
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from sources.declarative.decoders import GzipJsonDecoder


@pytest.mark.parametrize(
    "response_body, first_element",
    [("", {}), ("[]", {}), ('{"healthcheck": {"status": "ok"}}', {"healthcheck": {"status": "ok"}})],
)
def test_json_decoder(requests_mock, response_body, first_element):
    requests_mock.register_uri("GET", "https://airbyte.io/", text=response_body)
    response = requests.get("https://airbyte.io/")
    assert next(JsonDecoder(parameters={}).decode(response)) == first_element


@pytest.mark.parametrize(
    "response_body, expected_json",
    [
        ("", []),
        ('{"id": 1, "name": "test1"}', [{"id": 1, "name": "test1"}]),
        ('{"id": 1, "name": "test1"}\n{"id": 2, "name": "test2"}', [{"id": 1, "name": "test1"}, {"id": 2, "name": "test2"}]),
    ],
    ids=["empty_response", "one_line_json", "multi_line_json"],
)
def test_jsonl_decoder(requests_mock, response_body, expected_json):
    requests_mock.register_uri("GET", "https://airbyte.io/", text=response_body)
    response = requests.get("https://airbyte.io/")
    assert list(JsonlDecoder(parameters={}).decode(response)) == expected_json


@pytest.fixture(name="large_events_response")
def large_event_response_fixture():
    data = {"email": "email1@example.com"}
    jsonl_string = f"{json.dumps(data)}\n"
    lines_in_response = 2_000_000  # ≈ 58 MB of response
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = f"{dir_path}/test_response.txt"
    with open(file_path, "w") as file:
        for _ in range(lines_in_response):
            file.write(jsonl_string)
    yield (lines_in_response, file_path)
    os.remove(file_path)


@pytest.mark.slow
@pytest.mark.limit_memory("20 MB")
def test_jsonl_decoder_memory_usage(requests_mock, large_events_response):
    lines_in_response, file_path = large_events_response
    content = """
    name: users
    type: DeclarativeStream
    retriever:
      type: SimpleRetriever
      decoder:
        type: JsonlDecoder
      paginator:
        type: "NoPagination"
      requester:
        path: "users/{{ stream_slice.slice }}"
        type: HttpRequester
        url_base: "https://for-all-mankind.nasa.com/api/v1"
        http_method: GET
        authenticator:
          type: NoAuth
        request_headers: {}
        request_body_json: {}
      record_selector:
        type: RecordSelector
        extractor:
          type: DpathExtractor
          field_path: []
      partition_router:
        type: ListPartitionRouter
        cursor_field: "slice"
        values:
          - users1
          - users2
          - users3
          - users4
    primary_key: []
        """

    factory = ModelToComponentFactory()
    stream_manifest = YamlDeclarativeSource._parse(content)
    stream = factory.create_component(model_type=DeclarativeStreamModel, component_definition=stream_manifest, config={})

    def get_body():
        return open(file_path, "rb", buffering=30)

    counter = 0
    requests_mock.get("https://for-all-mankind.nasa.com/api/v1/users/users1", body=get_body())
    requests_mock.get("https://for-all-mankind.nasa.com/api/v1/users/users2", body=get_body())
    requests_mock.get("https://for-all-mankind.nasa.com/api/v1/users/users3", body=get_body())
    requests_mock.get("https://for-all-mankind.nasa.com/api/v1/users/users4", body=get_body())

    stream_slices = list(stream.stream_slices(sync_mode=SyncMode.full_refresh))
    for stream_slice in stream_slices:
        for _ in stream.retriever.read_records(records_schema={}, stream_slice=stream_slice):
            counter += 1

    assert counter == lines_in_response * len(stream_slices)

@pytest.mark.parametrize(
    "encoding",
    [
        "utf-8",
        "utf",
    ],
    ids=["utf-8", "utf"],
)
def test_gzipjson_decoder(requests_mock, encoding):
    response_to_compress = json.dumps([
        {
            "campaignId": 214078428,
            "campaignName": "sample-campaign-name-214078428",
            "adGroupId": "6490134",
            "adId": "665320125",
            "targetId": "791320341",
            "asin": "G000PSH142",
            "advertisedAsin": "G000PSH142",
            "keywordBid": "511234974",
            "keywordId": "965783021"
        },
        {
            "campaignId": 44504582,
            "campaignName": "sample-campaign-name-44504582",
            "adGroupId": "6490134",
            "adId": "665320125",
            "targetId": "791320341",
            "asin": "G000PSH142",
            "advertisedAsin": "G000PSH142",
            "keywordBid": "511234974",
            "keywordId": "965783021"
        },
        {
            "campaignId": 509144838,
            "campaignName": "sample-campaign-name-509144838",
            "adGroupId": "6490134",
            "adId": "665320125",
            "targetId": "791320341",
            "asin": "G000PSH142",
            "advertisedAsin": "G000PSH142",
            "keywordBid": "511234974",
            "keywordId": "965783021"
        },
        {
            "campaignId": 231712082,
            "campaignName": "sample-campaign-name-231712082",
            "adGroupId": "6490134",
            "adId": "665320125",
            "targetId": "791320341",
            "asin": "G000PSH142",
            "advertisedAsin": "G000PSH142",
            "keywordBid": "511234974",
            "keywordId": "965783021"
        },
        {
            "campaignId": 895306040,
            "campaignName": "sample-campaign-name-895306040",
            "adGroupId": "6490134",
            "adId": "665320125",
            "targetId": "791320341",
            "asin": "G000PSH142",
            "advertisedAsin": "G000PSH142",
            "keywordBid": "511234974",
            "keywordId": "965783021"
        }
    ])
    body = gzip.compress(response_to_compress.encode(encoding))

    requests_mock.register_uri("GET", "https://airbyte.io/", content=body)
    response = requests.get("https://airbyte.io/")
    assert len(list(GzipJsonDecoder(parameters={}, encoding=encoding).decode(response))) == 5
