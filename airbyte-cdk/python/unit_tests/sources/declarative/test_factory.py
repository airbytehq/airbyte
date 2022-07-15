#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import datetime

from airbyte_cdk.sources.declarative.datetime.min_max_datetime import MinMaxDatetime
from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.extractors.jello import JelloExtractor
from airbyte_cdk.sources.declarative.extractors.record_filter import RecordFilter
from airbyte_cdk.sources.declarative.extractors.record_selector import RecordSelector
from airbyte_cdk.sources.declarative.parsers.factory import DeclarativeComponentFactory
from airbyte_cdk.sources.declarative.parsers.yaml_parser import YamlParser
from airbyte_cdk.sources.declarative.requesters.error_handlers.composite_error_handler import CompositeErrorHandler
from airbyte_cdk.sources.declarative.requesters.error_handlers.default_error_handler import DefaultErrorHandler
from airbyte_cdk.sources.declarative.requesters.error_handlers.http_response_filter import HttpResponseFilter
from airbyte_cdk.sources.declarative.requesters.http_requester import HttpRequester
from airbyte_cdk.sources.declarative.requesters.paginators.next_page_url_paginator import NextPageUrlPaginator
from airbyte_cdk.sources.declarative.requesters.request_options.interpolated_request_options_provider import (
    InterpolatedRequestOptionsProvider,
)
from airbyte_cdk.sources.declarative.requesters.requester import HttpMethod
from airbyte_cdk.sources.declarative.retrievers.simple_retriever import SimpleRetriever
from airbyte_cdk.sources.declarative.schema.json_schema import JsonSchema
from airbyte_cdk.sources.declarative.stream_slicers.datetime_stream_slicer import DatetimeStreamSlicer
from airbyte_cdk.sources.declarative.transformations import AddFields, RemoveFields
from airbyte_cdk.sources.declarative.transformations.add_fields import AddedFieldDefinition
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
      class_name: airbyte_cdk.sources.declarative.auth.oauth.DeclarativeOauth2Authenticator
      client_id: "some_client_id"
      client_secret: "some_client_secret"
      token_refresh_endpoint: "https://api.sendgrid.com/v3/auth"
      refresh_token: "{{ config['apikey'] }}"
      refresh_request_body:
        body_field: "yoyoyo"
        interpolated_body_field: "{{ config['apikey'] }}"
    """
    config = parser.parse(content)
    authenticator = factory.create_component(config["authenticator"], input_config)()
    assert authenticator._client_id._string == "some_client_id"
    assert authenticator._client_secret._string == "some_client_secret"
    assert authenticator._token_refresh_endpoint._string == "https://api.sendgrid.com/v3/auth"
    assert authenticator._refresh_token._string == "verysecrettoken"
    assert authenticator._refresh_request_body._mapping == {"body_field": "yoyoyo", "interpolated_body_field": "{{ config['apikey'] }}"}


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


def test_datetime_stream_slicer():
    content = """
    stream_slicer:
        type: DatetimeStreamSlicer
        options:
          datetime_format: "%Y-%m-%d"
        start_datetime:
          type: MinMaxDatetime
          datetime: "{{ config['start_time'] }}"
          min_datetime: "{{ config['start_time'] + day_delta(2) }}"
        end_datetime: "{{ config['end_time'] }}"
        step: "10d"
        cursor_value: "created"
        lookback_window: "5d"
    """

    config = parser.parse(content)
    stream_slicer = factory.create_component(config["stream_slicer"], input_config)()
    assert type(stream_slicer) == DatetimeStreamSlicer
    assert stream_slicer._timezone == datetime.timezone.utc
    assert type(stream_slicer._start_datetime) == MinMaxDatetime
    assert type(stream_slicer._end_datetime) == MinMaxDatetime
    assert stream_slicer._start_datetime._datetime_format == "%Y-%m-%d"
    assert stream_slicer._start_datetime._timezone == datetime.timezone.utc
    assert stream_slicer._start_datetime._datetime_interpolator._string == "{{ config['start_time'] }}"
    assert stream_slicer._start_datetime._min_datetime_interpolator._string == "{{ config['start_time'] + day_delta(2) }}"
    assert stream_slicer._end_datetime._datetime_interpolator._string == "{{ config['end_time'] }}"
    assert stream_slicer._step == datetime.timedelta(days=10)
    assert stream_slicer._cursor_value._string == "created"
    assert stream_slicer._lookback_window._string == "5d"


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
  error_handler:
    type: DefaultErrorHandler
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
    file_path: "./source_sendgrid/schemas/{{ name }}.json"
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

    assert isinstance(stream._retriever._record_selector._extractor, JelloExtractor)

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
    assert stream._schema_loader._get_json_filepath() == "./source_sendgrid/schemas/lists.json"

    checker = factory.create_component(config["check"], input_config)()
    streams_to_check = checker._stream_names
    assert len(streams_to_check) == 1
    assert list(streams_to_check)[0] == "list_stream"

    assert stream._retriever._requester._path._default == "marketing/lists"


def test_create_record_selector():
    content = """
    extractor:
      type: JelloExtractor
      transform: "_"
    selector:
      class_name: airbyte_cdk.sources.declarative.extractors.record_selector.RecordSelector
      record_filter:
        class_name: airbyte_cdk.sources.declarative.extractors.record_filter.RecordFilter
        condition: "{{ record['id'] > stream_state['id'] }}"
      extractor:
        ref: "*ref(extractor)"
        transform: "_"
    """
    config = parser.parse(content)
    selector = factory.create_component(config["selector"], input_config)()
    assert isinstance(selector, RecordSelector)
    assert isinstance(selector._extractor, JelloExtractor)
    assert selector._extractor._transform == "_"
    assert isinstance(selector._record_filter, RecordFilter)


def test_create_requester():
    content = """
  requester:
    type: HttpRequester
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
    assert isinstance(component._error_handler, DefaultErrorHandler)
    assert component._path._string == "/v3/marketing/lists"
    assert component._url_base._string == "https://api.sendgrid.com"
    assert isinstance(component._authenticator, TokenAuthenticator)
    assert component._method == HttpMethod.GET
    assert component._request_options_provider._parameter_interpolator._interpolator._mapping["page_size"] == 10
    assert component._request_options_provider._headers_interpolator._interpolator._mapping["header"] == "header_value"
    assert component._name == "lists"


def test_create_composite_error_handler():
    content = """
        error_handler:
          type: "CompositeErrorHandler"
          error_handlers:
            - response_filters:
                - predicate: "{{ 'code' in decoded_response }}"
                  action: RETRY
            - response_filters:
                - http_codes: [ 403 ]
                  action: RETRY
    """
    config = parser.parse(content)
    component = factory.create_component(config["error_handler"], input_config)()
    assert len(component._error_handlers) == 2
    assert isinstance(component._error_handlers[0], DefaultErrorHandler)
    assert isinstance(component._error_handlers[0]._response_filters[0], HttpResponseFilter)
    assert component._error_handlers[0]._response_filters[0]._predicate._condition == "{{ 'code' in decoded_response }}"
    assert component._error_handlers[1]._response_filters[0]._http_codes == [403]
    assert isinstance(component, CompositeErrorHandler)


def test_config_with_defaults():
    content = """
    lists_stream:
      type: "DeclarativeStream"
      options:
        name: "lists"
        primary_key: id
        url_base: "https://api.sendgrid.com"
        schema_loader:
          file_path: "./source_sendgrid/schemas/{{name}}.yaml"
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
    assert stream._schema_loader._get_json_filepath() == "./source_sendgrid/schemas/lists.yaml"
    assert isinstance(stream._retriever._paginator, NextPageUrlPaginator)
    assert stream._retriever._paginator._url_base == "https://api.sendgrid.com"
    assert stream._retriever._paginator._interpolated_paginator._next_page_token_template._mapping == {
        "next_page_token": "{{ decoded_response.metadata.next}}"
    }


class TestCreateTransformations:
    # the tabbing matters
    base_options = """
                name: "lists"
                primary_key: id
                url_base: "https://api.sendgrid.com"
                schema_loader:
                  file_path: "./source_sendgrid/schemas/{{options.name}}.yaml"
                retriever:
                  requester:
                    path: "/v3/marketing/lists"
                    request_parameters:
                      page_size: 10
                  record_selector:
                    extractor:
                      transform: ".result[]"
    """

    def test_no_transformations(self):
        content = f"""
        the_stream:
            type: DeclarativeStream
            options:
                {self.base_options}
        """
        config = parser.parse(content)
        component = factory.create_component(config["the_stream"], input_config)()
        assert isinstance(component, DeclarativeStream)
        assert [] == component._transformations

    def test_remove_fields(self):
        content = f"""
        the_stream:
            type: DeclarativeStream
            options:
                {self.base_options}
                transformations:
                    - type: RemoveFields
                      field_pointers:
                        - ["path", "to", "field1"]
                        - ["path2"]
        """
        config = parser.parse(content)
        component = factory.create_component(config["the_stream"], input_config)()
        assert isinstance(component, DeclarativeStream)
        expected = [RemoveFields(field_pointers=[["path", "to", "field1"], ["path2"]])]
        assert expected == component._transformations

    def test_add_fields(self):
        content = f"""
        the_stream:
            class_name: airbyte_cdk.sources.declarative.declarative_stream.DeclarativeStream
            options:
                {self.base_options}
                transformations:
                    - type: AddFields
                      fields:
                        - path: ["field1"]
                          value: "static_value"
        """
        config = parser.parse(content)
        component = factory.create_component(config["the_stream"], input_config)()
        assert isinstance(component, DeclarativeStream)
        expected = [AddFields([AddedFieldDefinition(["field1"], "static_value")])]
        assert expected == component._transformations
