#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import datetime
from typing import List, Optional, Union

import pytest
from airbyte_cdk.sources.declarative.auth.token import BasicHttpAuthenticator
from airbyte_cdk.sources.declarative.datetime.min_max_datetime import MinMaxDatetime
from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.extractors.dpath_extractor import DpathExtractor
from airbyte_cdk.sources.declarative.extractors.record_filter import RecordFilter
from airbyte_cdk.sources.declarative.extractors.record_selector import RecordSelector
from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.parsers.factory import DeclarativeComponentFactory
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.sources.declarative.requesters.error_handlers import BackoffStrategy
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies import (
    ConstantBackoffStrategy,
    ExponentialBackoffStrategy,
    WaitTimeFromHeaderBackoffStrategy,
    WaitUntilTimeFromHeaderBackoffStrategy,
)
from airbyte_cdk.sources.declarative.requesters.error_handlers.composite_error_handler import CompositeErrorHandler
from airbyte_cdk.sources.declarative.requesters.error_handlers.default_error_handler import DefaultErrorHandler
from airbyte_cdk.sources.declarative.requesters.error_handlers.http_response_filter import HttpResponseFilter
from airbyte_cdk.sources.declarative.requesters.http_requester import HttpRequester
from airbyte_cdk.sources.declarative.requesters.paginators.default_paginator import DefaultPaginator
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption, RequestOptionType
from airbyte_cdk.sources.declarative.requesters.request_options.interpolated_request_options_provider import (
    InterpolatedRequestOptionsProvider,
)
from airbyte_cdk.sources.declarative.requesters.requester import HttpMethod
from airbyte_cdk.sources.declarative.retrievers.simple_retriever import SimpleRetriever
from airbyte_cdk.sources.declarative.schema import DefaultSchemaLoader, InlineSchemaLoader
from airbyte_cdk.sources.declarative.schema.json_file_schema_loader import JsonFileSchemaLoader
from airbyte_cdk.sources.declarative.stream_slicers.datetime_stream_slicer import DatetimeStreamSlicer
from airbyte_cdk.sources.declarative.stream_slicers.list_stream_slicer import ListStreamSlicer
from airbyte_cdk.sources.declarative.transformations import AddFields, RemoveFields
from airbyte_cdk.sources.declarative.transformations.add_fields import AddedFieldDefinition
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from jsonschema import ValidationError

factory = DeclarativeComponentFactory()

input_config = {"apikey": "verysecrettoken", "repos": ["airbyte", "airbyte-cloud"]}

resolver = ManifestReferenceResolver()


def test_factory():
    content = """
    limit: "50"
    offset_request_parameters:
      offset: "{{ next_page_token['offset'] }}"
      limit: "*ref(limit)"
    request_options:
      $options:
        here: "iam"
      class_name: airbyte_cdk.sources.declarative.requesters.request_options.interpolated_request_options_provider.InterpolatedRequestOptionsProvider
      request_parameters: "*ref(offset_request_parameters)"
      request_body_json:
        body_offset: "{{ next_page_token['offset'] }}"
    """
    config = resolver.preprocess_manifest(YamlDeclarativeSource._parse(content))

    factory.create_component(config["request_options"], input_config, False)

    request_options_provider = factory.create_component(config["request_options"], input_config)()

    assert type(request_options_provider) == InterpolatedRequestOptionsProvider
    assert request_options_provider._parameter_interpolator.config == input_config
    assert request_options_provider._parameter_interpolator._interpolator.mapping["offset"] == "{{ next_page_token['offset'] }}"
    assert request_options_provider._body_json_interpolator.config == input_config
    assert request_options_provider._body_json_interpolator._interpolator.mapping["body_offset"] == "{{ next_page_token['offset'] }}"


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
    config = resolver.preprocess_manifest(YamlDeclarativeSource._parse(content))

    factory.create_component(config["authenticator"], input_config, False)

    authenticator = factory.create_component(config["authenticator"], input_config)()
    assert authenticator.client_id.eval(input_config) == "some_client_id"
    assert authenticator.client_secret.string == "some_client_secret"

    assert authenticator.token_refresh_endpoint.eval(input_config) == "https://api.sendgrid.com/v3/auth"
    assert authenticator.refresh_token.eval(input_config) == "verysecrettoken"
    assert authenticator._refresh_request_body.mapping == {"body_field": "yoyoyo", "interpolated_body_field": "{{ config['apikey'] }}"}
    assert authenticator.get_refresh_request_body() == {"body_field": "yoyoyo", "interpolated_body_field": "verysecrettoken"}


def test_list_based_stream_slicer_with_values_refd():
    content = """
    repositories: ["airbyte", "airbyte-cloud"]
    stream_slicer:
      class_name: airbyte_cdk.sources.declarative.stream_slicers.list_stream_slicer.ListStreamSlicer
      slice_values: "*ref(repositories)"
      cursor_field: repository
    """
    config = resolver.preprocess_manifest(YamlDeclarativeSource._parse(content))

    factory.create_component(config["stream_slicer"], input_config, False)

    stream_slicer = factory.create_component(config["stream_slicer"], input_config)()
    assert ["airbyte", "airbyte-cloud"] == stream_slicer.slice_values


def test_list_based_stream_slicer_with_values_defined_in_config():
    content = """
    stream_slicer:
      type: ListStreamSlicer
      slice_values: "{{config['repos']}}"
      cursor_field: repository
      request_option:
        inject_into: header
        field_name: repository
    """
    config = resolver.preprocess_manifest(YamlDeclarativeSource._parse(content))

    factory.create_component(config["stream_slicer"], input_config, False)

    stream_slicer = factory.create_component(config["stream_slicer"], input_config)()
    assert ["airbyte", "airbyte-cloud"] == stream_slicer.slice_values
    assert stream_slicer.request_option.inject_into == RequestOptionType.header
    assert stream_slicer.request_option.field_name == "repository"


def test_create_substream_slicer():
    content = """
    schema_loader:
      file_path: "./source_sendgrid/schemas/{{ options['name'] }}.yaml"
      name: "{{ options['stream_name'] }}"
    retriever:
      requester:
        name: "{{ options['name'] }}"
        type: "HttpRequester"
        path: "kek"
      record_selector:
        extractor:
          field_pointer: []
    stream_A:
      type: DeclarativeStream
      $options:
        name: "A"
        primary_key: "id"
        retriever: "*ref(retriever)"
        url_base: "https://airbyte.io"
        schema_loader: "*ref(schema_loader)"
    stream_B:
      type: DeclarativeStream
      $options:
        name: "B"
        primary_key: "id"
        retriever: "*ref(retriever)"
        url_base: "https://airbyte.io"
        schema_loader: "*ref(schema_loader)"
    stream_slicer:
      type: SubstreamSlicer
      parent_stream_configs:
        - stream: "*ref(stream_A)"
          parent_key: id
          stream_slice_field: repository_id
          request_option:
            inject_into: request_parameter
            field_name: repository_id
        - stream: "*ref(stream_B)"
          parent_key: someid
          stream_slice_field: word_id
    """
    config = resolver.preprocess_manifest(YamlDeclarativeSource._parse(content))

    stream_slicer = factory.create_component(config["stream_slicer"], input_config)()
    parent_stream_configs = stream_slicer.parent_stream_configs
    assert len(parent_stream_configs) == 2
    assert isinstance(parent_stream_configs[0].stream, DeclarativeStream)
    assert isinstance(parent_stream_configs[1].stream, DeclarativeStream)
    assert stream_slicer.parent_stream_configs[0].parent_key == "id"
    assert stream_slicer.parent_stream_configs[0].stream_slice_field == "repository_id"
    assert stream_slicer.parent_stream_configs[0].request_option.inject_into == RequestOptionType.request_parameter
    assert stream_slicer.parent_stream_configs[0].request_option.field_name == "repository_id"

    assert stream_slicer.parent_stream_configs[1].parent_key == "someid"
    assert stream_slicer.parent_stream_configs[1].stream_slice_field == "word_id"
    assert stream_slicer.parent_stream_configs[1].request_option is None


def test_create_cartesian_stream_slicer():
    content = """
    stream_slicer_A:
      type: ListStreamSlicer
      slice_values: "{{config['repos']}}"
      cursor_field: repository
    stream_slicer_B:
      type: ListStreamSlicer
      slice_values:
        - hello
        - world
      cursor_field: words
    stream_slicer:
      type: CartesianProductStreamSlicer
      stream_slicers:
        - "*ref(stream_slicer_A)"
        - "*ref(stream_slicer_B)"
    """
    config = resolver.preprocess_manifest(YamlDeclarativeSource._parse(content))

    factory.create_component(config["stream_slicer"], input_config, False)

    stream_slicer = factory.create_component(config["stream_slicer"], input_config)()
    underlying_slicers = stream_slicer.stream_slicers
    assert len(underlying_slicers) == 2
    assert isinstance(underlying_slicers[0], ListStreamSlicer)
    assert isinstance(underlying_slicers[1], ListStreamSlicer)
    assert ["airbyte", "airbyte-cloud"] == underlying_slicers[0].slice_values
    assert ["hello", "world"] == underlying_slicers[1].slice_values


def test_datetime_stream_slicer():
    content = """
    stream_slicer:
        type: DatetimeStreamSlicer
        $options:
          datetime_format: "%Y-%m-%dT%H:%M:%S.%f%z"
          cursor_granularity: "PT0.000001S"
        start_datetime:
          type: MinMaxDatetime
          datetime: "{{ config['start_time'] }}"
          min_datetime: "{{ config['start_time'] + day_delta(2) }}"
        end_datetime: "{{ config['end_time'] }}"
        step: "P10D"
        cursor_field: "created"
        lookback_window: "P5D"
        start_time_option:
          inject_into: request_parameter
          field_name: created[gte]
    """

    config = resolver.preprocess_manifest(YamlDeclarativeSource._parse(content))

    factory.create_component(config["stream_slicer"], input_config, False)

    stream_slicer = factory.create_component(config["stream_slicer"], input_config)()
    assert type(stream_slicer) == DatetimeStreamSlicer
    assert stream_slicer._timezone == datetime.timezone.utc
    assert type(stream_slicer.start_datetime) == MinMaxDatetime
    assert type(stream_slicer.end_datetime) == MinMaxDatetime
    assert stream_slicer.start_datetime._datetime_format == "%Y-%m-%dT%H:%M:%S.%f%z"
    assert stream_slicer.start_datetime._timezone == datetime.timezone.utc
    assert stream_slicer.start_datetime.datetime.string == "{{ config['start_time'] }}"
    assert stream_slicer.start_datetime.min_datetime.string == "{{ config['start_time'] + day_delta(2) }}"
    assert stream_slicer.end_datetime.datetime.string == "{{ config['end_time'] }}"
    assert stream_slicer._step == datetime.timedelta(days=10)
    assert stream_slicer.cursor_field.string == "created"
    assert stream_slicer.cursor_granularity == "PT0.000001S"
    assert stream_slicer.lookback_window.string == "P5D"
    assert stream_slicer.start_time_option.inject_into == RequestOptionType.request_parameter
    assert stream_slicer.start_time_option.field_name == "created[gte]"


def test_full_config():
    content = """
decoder:
  class_name: "airbyte_cdk.sources.declarative.decoders.json_decoder.JsonDecoder"
extractor:
  class_name: airbyte_cdk.sources.declarative.extractors.dpath_extractor.DpathExtractor
  decoder: "*ref(decoder)"
selector:
  class_name: airbyte_cdk.sources.declarative.extractors.record_selector.RecordSelector
  record_filter:
    class_name: airbyte_cdk.sources.declarative.extractors.record_filter.RecordFilter
    condition: "{{ record['id'] > stream_state['id'] }}"
metadata_paginator:
    type: "DefaultPaginator"
    page_size_option:
      inject_into: request_parameter
      field_name: page_size
    page_token_option:
      inject_into: path
    pagination_strategy:
      type: "CursorPagination"
      cursor_value: "{{ response._metadata.next }}"
      page_size: 10
    url_base: "https://api.sendgrid.com/v3/"
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
    type: BearerAuthenticator
    api_token: "{{ config['apikey'] }}"
  request_parameters_provider: "*ref(request_options_provider)"
  error_handler:
    type: NoPagination
retriever:
  class_name: "airbyte_cdk.sources.declarative.retrievers.simple_retriever.SimpleRetriever"
  name: "{{ options['name'] }}"
  stream_slicer:
    class_name: airbyte_cdk.sources.declarative.stream_slicers.single_slice.SingleSlice
  paginator:
    class_name: airbyte_cdk.sources.declarative.requesters.paginators.no_pagination.NoPagination
  primary_key: "{{ options['primary_key'] }}"
partial_stream:
  class_name: "airbyte_cdk.sources.declarative.declarative_stream.DeclarativeStream"
  schema_loader:
    class_name: airbyte_cdk.sources.declarative.schema.json_file_schema_loader.JsonFileSchemaLoader
    file_path: "./source_sendgrid/schemas/{{ options.name }}.json"
  cursor_field: [ ]
list_stream:
  $ref: "*ref(partial_stream)"
  $options:
    name: "lists"
    primary_key: "id"
    extractor:
      $ref: "*ref(extractor)"
      field_pointer: ["{{ options['name'] }}"]
  retriever:
    $ref: "*ref(retriever)"
    requester:
      $ref: "*ref(requester)"
      path:
        $ref: "*ref(next_page_url_from_token_partial)"
        default: "marketing/lists"
    paginator:
      $ref: "*ref(metadata_paginator)"
    record_selector:
      $ref: "*ref(selector)"
check:
  class_name: airbyte_cdk.sources.declarative.checks.check_stream.CheckStream
  stream_names: ["list_stream"]
spec:
  class_name: airbyte_cdk.sources.declarative.spec.Spec
  documentation_url: https://airbyte.com/#yaml-from-manifest
  connection_specification:
    title: Test Spec
    type: object
    required:
      - api_key
    additionalProperties: false
    properties:
      api_key:
        type: string
        airbyte_secret: true
        title: API Key
        description: Test API Key
        order: 0
    """
    config = resolver.preprocess_manifest(YamlDeclarativeSource._parse(content))

    factory.create_component(config["list_stream"], input_config, False)

    stream_config = config["list_stream"]
    assert stream_config["class_name"] == "airbyte_cdk.sources.declarative.declarative_stream.DeclarativeStream"
    assert stream_config["cursor_field"] == []
    stream = factory.create_component(stream_config, input_config)()

    assert isinstance(stream.retriever.record_selector.extractor, DpathExtractor)

    assert type(stream) == DeclarativeStream
    assert stream.primary_key == "id"
    assert stream.name == "lists"
    assert type(stream.schema_loader) == JsonFileSchemaLoader
    assert type(stream.retriever) == SimpleRetriever
    assert stream.retriever.requester.http_method == HttpMethod.GET
    assert stream.retriever.requester.authenticator._token.eval(input_config) == "verysecrettoken"
    assert type(stream.retriever.record_selector) == RecordSelector
    assert type(stream.retriever.record_selector.extractor.decoder) == JsonDecoder

    assert [fp.eval(input_config) for fp in stream.retriever.record_selector.extractor.field_pointer] == ["lists"]
    assert type(stream.retriever.record_selector.record_filter) == RecordFilter
    assert stream.retriever.record_selector.record_filter._filter_interpolator.condition == "{{ record['id'] > stream_state['id'] }}"
    assert stream.schema_loader._get_json_filepath() == "./source_sendgrid/schemas/lists.json"

    checker = factory.create_component(config["check"], input_config)()
    streams_to_check = checker.stream_names
    assert len(streams_to_check) == 1
    assert list(streams_to_check)[0] == "list_stream"

    spec = factory.create_component(config["spec"], input_config)()
    documentation_url = spec.documentation_url
    connection_specification = spec.connection_specification
    assert documentation_url == "https://airbyte.com/#yaml-from-manifest"
    assert connection_specification["title"] == "Test Spec"
    assert connection_specification["required"] == ["api_key"]
    assert connection_specification["properties"]["api_key"] == {
        "type": "string",
        "airbyte_secret": True,
        "title": "API Key",
        "description": "Test API Key",
        "order": 0,
    }

    assert stream.retriever.requester.path.default == "marketing/lists"


@pytest.mark.parametrize(
    "test_name, record_selector, expected_runtime_selector",
    [("test_static_record_selector", "result", "result"), ("test_options_record_selector", "{{ options['name'] }}", "lists")],
)
def test_create_record_selector(test_name, record_selector, expected_runtime_selector):
    content = f"""
    extractor:
      type: DpathExtractor
    selector:
      $options:
        name: "lists"
      class_name: airbyte_cdk.sources.declarative.extractors.record_selector.RecordSelector
      record_filter:
        class_name: airbyte_cdk.sources.declarative.extractors.record_filter.RecordFilter
        condition: "{{ record['id'] > stream_state['id'] }}"
      extractor:
        $ref: "*ref(extractor)"
        field_pointer: ["{record_selector}"]
    """
    config = resolver.preprocess_manifest(YamlDeclarativeSource._parse(content))

    factory.create_component(config["selector"], input_config, False)

    selector = factory.create_component(config["selector"], input_config)()
    assert isinstance(selector, RecordSelector)
    assert isinstance(selector.extractor, DpathExtractor)
    assert [fp.eval(input_config) for fp in selector.extractor.field_pointer] == [expected_runtime_selector]
    assert isinstance(selector.record_filter, RecordFilter)


@pytest.mark.parametrize(
    "test_name, content, expected_field_pointer_value",
    [
        (
            "test_option_in_selector",
            """
                      extractor:
                        type: DpathExtractor
                        field_pointer: ["{{ options['name'] }}"]
                      selector:
                        class_name: airbyte_cdk.sources.declarative.extractors.record_selector.RecordSelector
                        $options:
                          name: "selector"
                        extractor: "*ref(extractor)"
                    """,
            "selector",
        ),
        (
            "test_option_in_extractor",
            """
                      extractor:
                        type: DpathExtractor
                        $options:
                          name: "extractor"
                        field_pointer: ["{{ options['name'] }}"]
                      selector:
                        class_name: airbyte_cdk.sources.declarative.extractors.record_selector.RecordSelector
                        $options:
                          name: "selector"
                        extractor: "*ref(extractor)"
                    """,
            "extractor",
        ),
    ],
)
def test_options_propagation(test_name, content, expected_field_pointer_value):
    config = resolver.preprocess_manifest(YamlDeclarativeSource._parse(content))

    selector = factory.create_component(config["selector"], input_config, True)()
    assert selector.extractor.field_pointer[0].eval(input_config) == expected_field_pointer_value


@pytest.mark.parametrize(
    "test_name, error_handler",
    [
        (
            "test_create_requester_constant_error_handler",
            """
  error_handler:
    backoff_strategies:
      - type: "ConstantBackoffStrategy"
        backoff_time_in_seconds: 5
            """,
        ),
        (
            "test_create_requester_exponential_error_handler",
            """
  error_handler:
    backoff_strategies:
      - type: "ExponentialBackoffStrategy"
        factor: 5
            """,
        ),
        (
            "test_create_requester_wait_time_from_header_error_handler",
            """
  error_handler:
    backoff_strategies:
      - type: "WaitTimeFromHeader"
        header: "a_header"
            """,
        ),
        (
            "test_create_requester_wait_time_until_from_header_error_handler",
            """
  error_handler:
    backoff_strategies:
      - type: "WaitUntilTimeFromHeader"
        header: "a_header"
            """,
        ),
        (
            "test_create_requester_no_error_handler",
            """""",
        ),
    ],
)
def test_create_requester(test_name, error_handler):
    content = f"""
  requester:
    type: HttpRequester
    path: "/v3/marketing/lists"
    $options:
        name: 'lists'
    url_base: "https://api.sendgrid.com"
    authenticator:
      type: "BasicHttpAuthenticator"
      username: "{{{{ options.name}}}}"
      password: "{{{{ config.apikey }}}}"
    request_options_provider:
      request_parameters:
        a_parameter: "something_here"
      request_headers:
        header: header_value
    {error_handler}
    """
    config = resolver.preprocess_manifest(YamlDeclarativeSource._parse(content))

    factory.create_component(config["requester"], input_config, False)

    component = factory.create_component(config["requester"], input_config)()
    assert isinstance(component, HttpRequester)
    assert isinstance(component.error_handler, DefaultErrorHandler)
    assert component.path.string == "/v3/marketing/lists"
    assert component.url_base.string == "https://api.sendgrid.com"
    assert isinstance(component.authenticator, BasicHttpAuthenticator)
    assert component.authenticator._username.eval(input_config) == "lists"
    assert component.authenticator._password.eval(input_config) == "verysecrettoken"
    assert component._method == HttpMethod.GET
    assert component._request_options_provider._parameter_interpolator._interpolator.mapping["a_parameter"] == "something_here"
    assert component._request_options_provider._headers_interpolator._interpolator.mapping["header"] == "header_value"
    assert component.name == "lists"


def test_create_composite_error_handler():
    content = """
        error_handler:
          type: "CompositeErrorHandler"
          error_handlers:
            - response_filters:
                - predicate: "{{ 'code' in response }}"
                  action: RETRY
            - response_filters:
                - http_codes: [ 403 ]
                  action: RETRY
    """
    config = resolver.preprocess_manifest(YamlDeclarativeSource._parse(content))

    factory.create_component(config["error_handler"], input_config, False)

    component = factory.create_component(config["error_handler"], input_config)()
    assert len(component.error_handlers) == 2
    assert isinstance(component.error_handlers[0], DefaultErrorHandler)
    assert isinstance(component.error_handlers[0].response_filters[0], HttpResponseFilter)
    assert component.error_handlers[0].response_filters[0].predicate.condition == "{{ 'code' in response }}"
    assert component.error_handlers[1].response_filters[0].http_codes == [403]
    assert isinstance(component, CompositeErrorHandler)


def test_config_with_defaults():
    content = """
    lists_stream:
      type: "DeclarativeStream"
      $options:
        name: "lists"
        primary_key: id
        url_base: "https://api.sendgrid.com"
        schema_loader:
          name: "{{ options.stream_name }}"
          file_path: "./source_sendgrid/schemas/{{ options.name }}.yaml"
        retriever:
          paginator:
            type: "DefaultPaginator"
            page_size_option:
              inject_into: request_parameter
              field_name: page_size
            page_token_option:
              inject_into: path
            pagination_strategy:
              type: "CursorPagination"
              cursor_value: "{{ response._metadata.next }}"
              page_size: 10
          requester:
            path: "/v3/marketing/lists"
            authenticator:
              type: "BearerAuthenticator"
              api_token: "{{ config.apikey }}"
            request_parameters:
              page_size: 10
          record_selector:
            extractor:
              field_pointer: ["result"]
    streams:
      - "*ref(lists_stream)"
    """
    config = resolver.preprocess_manifest(YamlDeclarativeSource._parse(content))

    factory.create_component(config["lists_stream"], input_config, False)

    stream_config = config["lists_stream"]
    stream = factory.create_component(stream_config, input_config)()
    assert type(stream) == DeclarativeStream
    assert stream.primary_key == "id"
    assert stream.name == "lists"
    assert type(stream.schema_loader) == DefaultSchemaLoader
    assert type(stream.retriever) == SimpleRetriever
    assert stream.retriever.requester.http_method == HttpMethod.GET

    assert stream.retriever.requester.authenticator._token.eval(input_config) == "verysecrettoken"
    assert [fp.eval(input_config) for fp in stream.retriever.record_selector.extractor.field_pointer] == ["result"]
    assert stream.schema_loader.get_json_schema() == {}
    assert isinstance(stream.retriever.paginator, DefaultPaginator)

    assert stream.retriever.paginator.url_base.string == "https://api.sendgrid.com"
    assert stream.retriever.paginator.pagination_strategy.get_page_size() == 10


def test_create_default_paginator():
    content = """
      paginator:
        type: "DefaultPaginator"
        url_base: "https://airbyte.io"
        page_size_option:
          inject_into: request_parameter
          field_name: page_size
        page_token_option:
          inject_into: path
        pagination_strategy:
          type: "CursorPagination"
          page_size: 50
          cursor_value: "{{ response._metadata.next }}"
    """
    config = resolver.preprocess_manifest(YamlDeclarativeSource._parse(content))

    factory.create_component(config["paginator"], input_config, False)

    paginator_config = config["paginator"]
    paginator = factory.create_component(paginator_config, input_config)()
    assert isinstance(paginator, DefaultPaginator)
    page_token_option = paginator.page_token_option
    assert isinstance(page_token_option, RequestOption)
    assert page_token_option.inject_into == RequestOptionType.path


class TestCreateTransformations:
    # the tabbing matters
    base_options = """
                name: "lists"
                primary_key: id
                url_base: "https://api.sendgrid.com"
                schema_loader:
                  name: "{{ options.name }}"
                  file_path: "./source_sendgrid/schemas/{{ options.name }}.yaml"
                retriever:
                  requester:
                    name: "{{ options.name }}"
                    path: "/v3/marketing/lists"
                    request_parameters:
                      page_size: 10
                  record_selector:
                    extractor:
                      field_pointer: ["result"]
    """

    def test_no_transformations(self):
        content = f"""
        the_stream:
            type: DeclarativeStream
            $options:
                {self.base_options}
        """
        config = resolver.preprocess_manifest(YamlDeclarativeSource._parse(content))

        factory.create_component(config["the_stream"], input_config, False)

        component = factory.create_component(config["the_stream"], input_config)()
        assert isinstance(component, DeclarativeStream)
        assert [] == component.transformations

    def test_remove_fields(self):
        content = f"""
        the_stream:
            type: DeclarativeStream
            $options:
                {self.base_options}
                transformations:
                    - type: RemoveFields
                      field_pointers:
                        - ["path", "to", "field1"]
                        - ["path2"]
        """
        config = resolver.preprocess_manifest(YamlDeclarativeSource._parse(content))

        factory.create_component(config["the_stream"], input_config, False)

        component = factory.create_component(config["the_stream"], input_config)()
        assert isinstance(component, DeclarativeStream)
        expected = [RemoveFields(field_pointers=[["path", "to", "field1"], ["path2"]], options={})]
        assert expected == component.transformations

    def test_add_fields(self):
        content = f"""
        the_stream:
            class_name: airbyte_cdk.sources.declarative.declarative_stream.DeclarativeStream
            $options:
                {self.base_options}
                transformations:
                    - type: AddFields
                      fields:
                        - path: ["field1"]
                          value: "static_value"
        """
        config = resolver.preprocess_manifest(YamlDeclarativeSource._parse(content))

        factory.create_component(config["the_stream"], input_config, False)

        component = factory.create_component(config["the_stream"], input_config)()
        assert isinstance(component, DeclarativeStream)
        expected = [
            AddFields(
                fields=[
                    AddedFieldDefinition(
                        path=["field1"], value=InterpolatedString(string="static_value", default="static_value", options={}), options={}
                    )
                ],
                options={},
            )
        ]
        assert expected == component.transformations

    def test_forward_references(self):
        content = f"""
        the_stream:
            type: DeclarativeStream
            $options:
                {self.base_options}
            schema_loader:
                type: InlineSchemaLoader
                schema: "*ref(schemas.the_stream_schema)"
        schemas:
            the_stream_schema:
                type: object
                properties:
                    title:
                        type: string
        """
        config = resolver.preprocess_manifest(YamlDeclarativeSource._parse(content))

        factory.create_component(config["the_stream"], input_config, False)

        component = factory.create_component(config["the_stream"], input_config)()
        assert isinstance(component.schema_loader, InlineSchemaLoader)
        expected = {"type": "object", "properties": {"title": {"type": "string"}}}
        assert expected == component.schema_loader.schema


def test_validation_wrong_input_type():
    content = """
    extractor:
      type: DpathExtractor
    selector:
      class_name: airbyte_cdk.sources.declarative.extractors.record_selector.RecordSelector
      record_filter:
        class_name: airbyte_cdk.sources.declarative.extractors.record_filter.RecordFilter
        condition: "{{ record['id'] > stream_state['id'] }}"
      extractor:
        $ref: "*ref(extractor)"
        field_pointer: 408
    """
    config = resolver.preprocess_manifest(YamlDeclarativeSource._parse(content))
    with pytest.raises(ValidationError):
        factory.create_component(config["selector"], input_config, False)


def test_validation_type_missing_required_fields():
    content = """
    stream_slicer:
      type: DatetimeStreamSlicer
      $options:
        datetime_format: "%Y-%m-%dT%H:%M:%S.%f%z"
      start_datetime:
        type: MinMaxDatetime
        datetime: "{{ config['start_time'] }}"
        min_datetime: "{{ config['start_time'] + day_delta(2) }}"
      end_datetime: "{{ config['end_time'] }}"
      cursor_field: "created"
      lookback_window: "P5D"
      start_time_option:
        inject_into: request_parameter
        field_name: created[gte]
    """

    config = resolver.preprocess_manifest(YamlDeclarativeSource._parse(content))
    with pytest.raises(ValidationError):
        factory.create_component(config["stream_slicer"], input_config, False)


def test_validation_wrong_interface_type():
    content = """
    paginator:
      type: "DefaultPaginator"
      page_size: 10
      url_base: "https://airbyte.io"
      page_size_option:
        inject_into: request_parameter
        field_name: page_size
      page_token_option:
        inject_into: path
      pagination_strategy:
        type: "MinMaxDatetime"
        datetime: "{{ response._metadata.next }}"
    """
    config = resolver.preprocess_manifest(YamlDeclarativeSource._parse(content))
    with pytest.raises(ValidationError):
        factory.create_component(config["paginator"], input_config, False)


def test_validation_create_composite_error_handler():
    content = """
        error_handler:
          type: "CompositeErrorHandler"
          error_handlers:
            - response_filters:
                - predicate: "{{ 'code' in response }}"
                  action: RETRY
            - response_filters:
                - http_codes: [ 403 ]
    """
    config = resolver.preprocess_manifest(YamlDeclarativeSource._parse(content))
    with pytest.raises(ValidationError):
        factory.create_component(config["error_handler"], input_config, False)


# Leaving this test here to document a limitation of the validator. Decoder has no meaningful fields to validate on so it accepts
# the MinMaxDatetime despite being the wrong type
def test_validation_wrong_object_type():
    content = """
      paginator:
        type: "DefaultPaginator"
        page_size: 10
        url_base: "https://airbyte.io"
        page_size_option:
          inject_into: request_parameter
          field_name: page_size
        page_token_option:
          inject_into: path
        pagination_strategy:
          type: "CursorPagination"
          cursor_value: "{{ response._metadata.next }}"
        decoder:
          type: "MinMaxDatetime"
          datetime: "{{ response._metadata.next }}"
    """
    config = resolver.preprocess_manifest(YamlDeclarativeSource._parse(content))
    factory.create_component(config["paginator"], input_config, False)


# This test should fail because the extractor doesn't match the Array of resolved classes. However, despite the schema being correct
# validation passes. Leaving this here to document it and revisit at another time. This is another validator limitation.
def test_validate_types_nested_in_list():
    content = """
    error_handler:
      type: DefaultErrorHandler
      backoff_strategies:
        - type: DpathExtractor
          field_pointer: ["result"]
    """
    config = resolver.preprocess_manifest(YamlDeclarativeSource._parse(content))
    factory.create_component(config["error_handler"], input_config, False)


@pytest.mark.parametrize(
    "test_name, input_type, expected_unpacked_types",
    [
        (
            "test_unpacking_component_in_list",
            List[BackoffStrategy],
            List[
                Union[
                    ConstantBackoffStrategy,
                    ExponentialBackoffStrategy,
                    WaitTimeFromHeaderBackoffStrategy,
                    WaitUntilTimeFromHeaderBackoffStrategy,
                ]
            ],
        ),
        (
            "test_unpacking_component_in_union",
            Union[BackoffStrategy, RequestOption],
            Union[
                ConstantBackoffStrategy,
                ExponentialBackoffStrategy,
                WaitTimeFromHeaderBackoffStrategy,
                WaitUntilTimeFromHeaderBackoffStrategy,
                RequestOption,
            ],
        ),
        (
            "test_unpacking_component_in_optional",
            Optional[BackoffStrategy],
            Union[
                ConstantBackoffStrategy,
                ExponentialBackoffStrategy,
                WaitTimeFromHeaderBackoffStrategy,
                WaitUntilTimeFromHeaderBackoffStrategy,
                type(None),
            ],
        ),
        (
            "test_unpacking_component_nested_in_multiple_types",
            Optional[List[BackoffStrategy]],
            Union[
                List[
                    Union[
                        ConstantBackoffStrategy,
                        ExponentialBackoffStrategy,
                        WaitTimeFromHeaderBackoffStrategy,
                        WaitUntilTimeFromHeaderBackoffStrategy,
                    ]
                ],
                type(None),
            ],
        ),
    ],
)
def test_unpack(test_name, input_type, expected_unpacked_types):
    actual_unpacked_types = DeclarativeComponentFactory.unpack(input_type)
    assert actual_unpacked_types == expected_unpacked_types
