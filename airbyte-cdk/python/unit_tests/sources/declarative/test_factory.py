#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.extractors.record_filter import RecordFilter
from airbyte_cdk.sources.declarative.extractors.record_selector import RecordSelector
from airbyte_cdk.sources.declarative.parsers.factory import DeclarativeComponentFactory
from airbyte_cdk.sources.declarative.parsers.yaml_parser import YamlParser
from airbyte_cdk.sources.declarative.requesters.http_requester import HttpRequester
from airbyte_cdk.sources.declarative.requesters.paginators.next_page_url_paginator import NextPageUrlPaginator
from airbyte_cdk.sources.declarative.requesters.request_options.interpolated_request_options_provider import (
    InterpolatedRequestOptionsProvider,
)
from airbyte_cdk.sources.declarative.requesters.requester import HttpMethod
from airbyte_cdk.sources.declarative.requesters.retriers.default_retrier import DefaultRetrier
from airbyte_cdk.sources.declarative.retrievers.simple_retriever import SimpleRetriever
from airbyte_cdk.sources.declarative.schema.json_schema import JsonSchema
from airbyte_cdk.sources.streams.http.requests_native_auth.token import TokenAuthenticator

factory = DeclarativeComponentFactory()

parser = YamlParser()

input_config = {"apikey": "verysecrettoken", "repos": ["airbyte", "airbyte-cloud"]}


def test_factory():
    content = """
    limit: 50
    offset_request_parameters:
      offset: "{{ next_page_token['offset'] }}"
      limit: "*ref(limit)"
    request_options:
      class_name: airbyte_cdk.sources.declarative.requesters.request_options.interpolated_request_options_provider.InterpolatedRequestOptionsProvider
      request_parameters: "*ref(offset_request_parameters)"
      request_body_json:
        body_offset: "{{ next_page_token['offset'] }}"
    """
    config = parser.parse(content)
    request_options_provider = factory.create_component(config["request_options"], input_config)()
    assert type(request_options_provider) == InterpolatedRequestOptionsProvider
    assert request_options_provider._parameter_interpolator._config == input_config
    assert request_options_provider._parameter_interpolator._interpolator._mapping["offset"] == "{{ next_page_token['offset'] }}"
    assert request_options_provider._body_json_interpolator._config == input_config
    assert request_options_provider._body_json_interpolator._interpolator._mapping["body_offset"] == "{{ next_page_token['offset'] }}"


def test_interpolate_config():
    content = """
authenticator:
  class_name: airbyte_cdk.sources.streams.http.requests_native_auth.token.TokenAuthenticator
  token: "{{ config['apikey'] }}"
    """
    config = parser.parse(content)
    authenticator = factory.create_component(config["authenticator"], input_config)()
    assert authenticator._tokens == ["verysecrettoken"]


def test_list_based_stream_slicer_with_values_refd():
    content = """
    repositories: ["airbyte", "airbyte-cloud"]
    stream_slicer:
      class_name: airbyte_cdk.sources.declarative.stream_slicers.list_stream_slicer.ListStreamSlicer
      slice_values: "*ref(repositories)"
      slice_definition:
        repository: "{{ slice_value }}"
    """
    config = parser.parse(content)
    stream_slicer = factory.create_component(config["stream_slicer"], input_config)()
    assert ["airbyte", "airbyte-cloud"] == stream_slicer._slice_values


def test_list_based_stream_slicer_with_values_defined_in_config():
    content = """
    stream_slicer:
      class_name: airbyte_cdk.sources.declarative.stream_slicers.list_stream_slicer.ListStreamSlicer
      slice_values: "{{config['repos']}}"
      slice_definition:
        repository: "{{ slice_value }}"
    """
    config = parser.parse(content)
    stream_slicer = factory.create_component(config["stream_slicer"], input_config)()
    assert ["airbyte", "airbyte-cloud"] == stream_slicer._slice_values


def test_full_config():
    content = """
decoder:
  class_name: "airbyte_cdk.sources.declarative.decoders.json_decoder.JsonDecoder"
extractor:
  class_name: airbyte_cdk.sources.declarative.extractors.jello.JelloExtractor
  decoder: "*ref(decoder)"
selector:
  class_name: airbyte_cdk.sources.declarative.extractors.record_selector.RecordSelector
  record_filter:
    class_name: airbyte_cdk.sources.declarative.extractors.record_filter.RecordFilter
    condition: "{{ record['id'] > stream_state['id'] }}"
metadata_paginator:
  class_name: "airbyte_cdk.sources.declarative.requesters.paginators.next_page_url_paginator.NextPageUrlPaginator"
  next_page_token_template:
    "next_page_url": "{{ decoded_response['_metadata']['next'] }}"
next_page_url_from_token_partial:
  class_name: "airbyte_cdk.sources.declarative.interpolation.interpolated_string.InterpolatedString"
  string: "{{ next_page_token['next_page_url'] }}"
request_options_provider:
  class_name: airbyte_cdk.sources.declarative.requesters.request_options.interpolated_request_options_provider.InterpolatedRequestOptionsProvider
requester:
  class_name: airbyte_cdk.sources.declarative.requesters.http_requester.HttpRequester
  name: "{{ options['name'] }}"
  url_base: "https://api.sendgrid.com/v3/"
  http_method: "GET"
  authenticator:
    class_name: airbyte_cdk.sources.streams.http.requests_native_auth.token.TokenAuthenticator
    token: "{{ config['apikey'] }}"
  request_parameters_provider: "*ref(request_options_provider)"
  retrier:
    class_name: airbyte_cdk.sources.declarative.requesters.retriers.default_retrier.DefaultRetrier
retriever:
  class_name: "airbyte_cdk.sources.declarative.retrievers.simple_retriever.SimpleRetriever"
  name: "{{ options['name'] }}"
  state:
    class_name: airbyte_cdk.sources.declarative.states.dict_state.DictState
  stream_slicer:
    class_name: airbyte_cdk.sources.declarative.stream_slicers.single_slice.SingleSlice
  paginator:
    class_name: airbyte_cdk.sources.declarative.requesters.paginators.no_pagination.NoPagination
  primary_key: "{{ options['primary_key'] }}"
partial_stream:
  class_name: "airbyte_cdk.sources.declarative.declarative_stream.DeclarativeStream"
  schema_loader:
    class_name: airbyte_cdk.sources.declarative.schema.json_schema.JsonSchema
    file_path: "./source_sendgrid/schemas/{{options['name']}}.json"
  cursor_field: [ ]
list_stream:
  ref: "*ref(partial_stream)"
  options:
    name: "lists"
    primary_key: "id"
    extractor:
      ref: "*ref(extractor)"
      transform: ".result[]"
  retriever:
    ref: "*ref(retriever)"
    requester:
      ref: "*ref(requester)"
      path:
        ref: "*ref(next_page_url_from_token_partial)"
        default: "marketing/lists"
    paginator:
      ref: "*ref(metadata_paginator)"
    record_selector:
      ref: "*ref(selector)"
check:
  class_name: airbyte_cdk.sources.declarative.checks.check_stream.CheckStream
  stream_names: ["list_stream"]
    """
    config = parser.parse(content)

    stream_config = config["list_stream"]
    assert stream_config["class_name"] == "airbyte_cdk.sources.declarative.declarative_stream.DeclarativeStream"
    assert stream_config["cursor_field"] == []
    stream = factory.create_component(stream_config, input_config)()
    assert type(stream) == DeclarativeStream
    assert stream.primary_key == "id"
    assert stream.name == "lists"
    assert type(stream._schema_loader) == JsonSchema
    assert type(stream._retriever) == SimpleRetriever
    assert stream._retriever._requester._method == HttpMethod.GET
    assert stream._retriever._requester._authenticator._tokens == ["verysecrettoken"]
    assert type(stream._retriever._record_selector) == RecordSelector
    assert type(stream._retriever._record_selector._extractor._decoder) == JsonDecoder
    assert stream._retriever._record_selector._extractor._transform == ".result[]"
    assert type(stream._retriever._record_selector._record_filter) == RecordFilter
    assert stream._retriever._record_selector._record_filter._filter_interpolator._condition == "{{ record['id'] > stream_state['id'] }}"
    assert stream._schema_loader._file_path._string == "./source_sendgrid/schemas/lists.json"

    checker = factory.create_component(config["check"], input_config)()
    streams_to_check = checker._stream_names
    assert len(streams_to_check) == 1
    assert list(streams_to_check)[0] == "list_stream"

    assert stream._retriever._requester._path._default == "marketing/lists"


def test_create_requester():
    content = """
  requester:
    class_name: airbyte_cdk.sources.declarative.requesters.http_requester.HttpRequester
    path: "/v3/marketing/lists"
    name: lists
    url_base: "https://api.sendgrid.com"
    authenticator:
      type: "TokenAuthenticator"
      token: "{{ config.apikey }}"
    request_options_provider:
      request_parameters:
        page_size: 10
      request_headers:
        header: header_value
    """
    config = parser.parse(content)
    component = factory.create_component(config["requester"], input_config)()
    assert isinstance(component, HttpRequester)
    assert isinstance(component._retrier, DefaultRetrier)
    assert component._path._string == "/v3/marketing/lists"
    assert component._url_base._string == "https://api.sendgrid.com"
    assert isinstance(component._authenticator, TokenAuthenticator)
    assert component._method == HttpMethod.GET
    assert component._request_options_provider._parameter_interpolator._interpolator._mapping["page_size"] == 10
    assert component._request_options_provider._headers_interpolator._interpolator._mapping["header"] == "header_value"
    assert component._name == "lists"


def test_full_config_with_defaults():
    content = """
    lists_stream:
      class_name: "airbyte_cdk.sources.declarative.declarative_stream.DeclarativeStream"
      options:
        name: "lists"
        primary_key: id
        url_base: "https://api.sendgrid.com"
        schema_loader:
          file_path: "./source_sendgrid/schemas/{{options.name}}.yaml"
        retriever:
          paginator:
            type: "NextPageUrlPaginator"
            next_page_token_template:
                next_page_token: "{{ decoded_response.metadata.next}}"
          requester:
            path: "/v3/marketing/lists"
            authenticator:
              type: "TokenAuthenticator"
              token: "{{ config.apikey }}"
            request_parameters:
              page_size: 10
          record_selector:
            extractor:
              transform: ".result[]"
    streams:
      - "*ref(lists_stream)"
    """
    config = parser.parse(content)

    stream_config = config["lists_stream"]
    stream = factory.create_component(stream_config, input_config)()
    assert type(stream) == DeclarativeStream
    assert stream.primary_key == "id"
    assert stream.name == "lists"
    assert type(stream._schema_loader) == JsonSchema
    assert type(stream._retriever) == SimpleRetriever
    assert stream._retriever._requester._method == HttpMethod.GET
    assert stream._retriever._requester._authenticator._tokens == ["verysecrettoken"]
    assert stream._retriever._record_selector._extractor._transform == ".result[]"
    assert stream._schema_loader._file_path._string == "./source_sendgrid/schemas/lists.yaml"
    assert isinstance(stream._retriever._paginator, NextPageUrlPaginator)
    assert stream._retriever._paginator._url_base == "https://api.sendgrid.com"
    assert stream._retriever._paginator._interpolated_paginator._next_page_token_template._mapping == {
        "next_page_token": "{{ decoded_response.metadata.next}}"
    }
