#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import datetime

import pytest
from airbyte_cdk.sources.declarative.auth import DeclarativeOauth2Authenticator
from airbyte_cdk.sources.declarative.auth.token import BasicHttpAuthenticator, BearerAuthenticator
from airbyte_cdk.sources.declarative.checks import CheckStream
from airbyte_cdk.sources.declarative.datetime import MinMaxDatetime
from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream
from airbyte_cdk.sources.declarative.decoders import JsonDecoder
from airbyte_cdk.sources.declarative.extractors import DpathExtractor, RecordFilter, RecordSelector
from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.models import CartesianProductStreamSlicer as CartesianProductStreamSlicerModel
from airbyte_cdk.sources.declarative.models import CheckStream as CheckStreamModel
from airbyte_cdk.sources.declarative.models import CompositeErrorHandler as CompositeErrorHandlerModel
from airbyte_cdk.sources.declarative.models import DatetimeStreamSlicer as DatetimeStreamSlicerModel
from airbyte_cdk.sources.declarative.models import DeclarativeStream as DeclarativeStreamModel
from airbyte_cdk.sources.declarative.models import DefaultPaginator as DefaultPaginatorModel
from airbyte_cdk.sources.declarative.models import HttpRequester as HttpRequesterModel
from airbyte_cdk.sources.declarative.models import ListStreamSlicer as ListStreamSlicerModel
from airbyte_cdk.sources.declarative.models import OAuthAuthenticator as OAuthAuthenticatorModel
from airbyte_cdk.sources.declarative.models import RecordSelector as RecordSelectorModel
from airbyte_cdk.sources.declarative.models import Spec as SpecModel
from airbyte_cdk.sources.declarative.models import SubstreamSlicer as SubstreamSlicerModel
from airbyte_cdk.sources.declarative.parsers.manifest_component_transformer import ManifestComponentTransformer
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.declarative.requesters import HttpRequester
from airbyte_cdk.sources.declarative.requesters.error_handlers import CompositeErrorHandler, DefaultErrorHandler, HttpResponseFilter
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies import (
    ConstantBackoffStrategy,
    ExponentialBackoffStrategy,
    WaitTimeFromHeaderBackoffStrategy,
    WaitUntilTimeFromHeaderBackoffStrategy,
)
from airbyte_cdk.sources.declarative.requesters.error_handlers.response_action import ResponseAction
from airbyte_cdk.sources.declarative.requesters.paginators import DefaultPaginator
from airbyte_cdk.sources.declarative.requesters.paginators.strategies import CursorPaginationStrategy
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption, RequestOptionType
from airbyte_cdk.sources.declarative.requesters.request_options import InterpolatedRequestOptionsProvider
from airbyte_cdk.sources.declarative.requesters.requester import HttpMethod
from airbyte_cdk.sources.declarative.retrievers import SimpleRetriever
from airbyte_cdk.sources.declarative.schema import JsonFileSchemaLoader
from airbyte_cdk.sources.declarative.spec import Spec
from airbyte_cdk.sources.declarative.stream_slicers import (
    CartesianProductStreamSlicer,
    DatetimeStreamSlicer,
    ListStreamSlicer,
    SubstreamSlicer,
)
from airbyte_cdk.sources.declarative.transformations import AddFields, RemoveFields
from airbyte_cdk.sources.declarative.transformations.add_fields import AddedFieldDefinition
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from dateutil.relativedelta import relativedelta

factory = ModelToComponentFactory()

resolver = ManifestReferenceResolver()

transformer = ManifestComponentTransformer()

input_config = {"apikey": "verysecrettoken", "repos": ["airbyte", "airbyte-cloud"]}


def test_full_config_stream():
    content = """
decoder:
  type: JsonDecoder
extractor:
  type: DpathExtractor
  decoder: "*ref(decoder)"
selector:
  type: RecordSelector
  record_filter:
    type: RecordFilter
    condition: "{{ record['id'] > stream_state['id'] }}"
metadata_paginator:
    type: DefaultPaginator
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
request_options_provider:
  type: InterpolatedRequestOptionsProvider
  request_parameters:
    unit: "day"
requester:
  type: HttpRequester
  name: "{{ options['name'] }}"
  url_base: "https://api.sendgrid.com/v3/"
  http_method: "GET"
  authenticator:
    type: BearerAuthenticator
    api_token: "{{ config['apikey'] }}"
  request_options_provider: "*ref(request_options_provider)"
retriever:
  name: "{{ options['name'] }}"
  stream_slicer:
    type: SingleSlice
  paginator:
    type: NoPagination
  primary_key: "{{ options['primary_key'] }}"
partial_stream:
  type: DeclarativeStream
  schema_loader:
    type: JsonFileSchemaLoader
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
      path: "{{ next_page_token['next_page_url'] }}"
    paginator:
      $ref: "*ref(metadata_paginator)"
    record_selector:
      $ref: "*ref(selector)"
  transformations:
    - type: AddFields
      fields:
      - path: ["extra"]
        value: "{{ response.to_add }}"
check:
  type: CheckStream
  stream_names: ["list_stream"]
spec:
  type: Spec
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
    parsed_manifest = YamlDeclarativeSource._parse(content)
    resolved_manifest = resolver.preprocess_manifest(parsed_manifest, {}, "")
    resolved_manifest["type"] = "DeclarativeSource"
    config = transformer.propagate_types_and_options("", resolved_manifest, {})

    stream_config = config["list_stream"]
    assert stream_config["type"] == "DeclarativeStream"
    assert stream_config["cursor_field"] == []
    stream = factory.create_component(model_type=DeclarativeStreamModel, component_definition=stream_config, config=input_config)

    assert isinstance(stream, DeclarativeStream)
    assert stream.primary_key == "id"
    assert stream.name == "lists"

    assert isinstance(stream.schema_loader, JsonFileSchemaLoader)
    assert stream.schema_loader._get_json_filepath() == "./source_sendgrid/schemas/lists.json"

    assert len(stream.transformations) == 1
    add_fields = stream.transformations[0]
    assert isinstance(add_fields, AddFields)
    assert add_fields.fields[0].path == ["extra"]
    assert add_fields.fields[0].value.string == "{{ response.to_add }}"

    assert isinstance(stream.retriever, SimpleRetriever)
    assert stream.retriever.primary_key == "{{ options['primary_key'] }}"
    assert stream.retriever.name == "lists"

    assert isinstance(stream.retriever.record_selector, RecordSelector)

    assert isinstance(stream.retriever.record_selector.extractor, DpathExtractor)
    assert isinstance(stream.retriever.record_selector.extractor.decoder, JsonDecoder)
    assert [fp.eval(input_config) for fp in stream.retriever.record_selector.extractor.field_pointer] == ["lists"]

    assert isinstance(stream.retriever.record_selector.record_filter, RecordFilter)
    assert stream.retriever.record_selector.record_filter._filter_interpolator.condition == "{{ record['id'] > stream_state['id'] }}"

    assert isinstance(stream.retriever.paginator, DefaultPaginator)
    assert isinstance(stream.retriever.paginator.decoder, JsonDecoder)
    assert stream.retriever.paginator.page_size_option.field_name == "page_size"
    assert stream.retriever.paginator.page_size_option.inject_into == RequestOptionType.request_parameter
    assert stream.retriever.paginator.page_token_option.inject_into == RequestOptionType.path
    assert stream.retriever.paginator.url_base.string == "https://api.sendgrid.com/v3/"
    assert stream.retriever.paginator.url_base.default == "https://api.sendgrid.com/v3/"

    assert isinstance(stream.retriever.paginator.pagination_strategy, CursorPaginationStrategy)
    assert isinstance(stream.retriever.paginator.pagination_strategy.decoder, JsonDecoder)
    assert stream.retriever.paginator.pagination_strategy.cursor_value.string == "{{ response._metadata.next }}"
    assert stream.retriever.paginator.pagination_strategy.cursor_value.default == "{{ response._metadata.next }}"
    assert stream.retriever.paginator.pagination_strategy.page_size == 10

    assert isinstance(stream.retriever.requester, HttpRequester)
    assert stream.retriever.requester.http_method == HttpMethod.GET
    assert stream.retriever.requester.path.string == "{{ next_page_token['next_page_url'] }}"
    assert stream.retriever.requester.path.default == "{{ next_page_token['next_page_url'] }}"

    assert isinstance(stream.retriever.requester.authenticator, BearerAuthenticator)
    assert stream.retriever.requester.authenticator._token.eval(input_config) == "verysecrettoken"

    assert isinstance(stream.retriever.requester.request_options_provider, InterpolatedRequestOptionsProvider)
    assert stream.retriever.requester.request_options_provider.request_parameters.get("unit") == "day"

    checker = factory.create_component(model_type=CheckStreamModel, component_definition=config["check"], config=input_config)

    assert isinstance(checker, CheckStream)
    streams_to_check = checker.stream_names
    assert len(streams_to_check) == 1
    assert list(streams_to_check)[0] == "list_stream"

    spec = factory.create_component(model_type=SpecModel, component_definition=config["spec"], config=input_config)

    assert isinstance(spec, Spec)
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


def test_interpolate_config():
    content = """
    authenticator:
      type: OAuthAuthenticator
      client_id: "some_client_id"
      client_secret: "some_client_secret"
      token_refresh_endpoint: "https://api.sendgrid.com/v3/auth"
      refresh_token: "{{ config['apikey'] }}"
      refresh_request_body:
        body_field: "yoyoyo"
        interpolated_body_field: "{{ config['apikey'] }}"
    """
    parsed_manifest = YamlDeclarativeSource._parse(content)
    resolved_manifest = resolver.preprocess_manifest(parsed_manifest, {}, "")
    authenticator_config = transformer.propagate_types_and_options("", resolved_manifest["authenticator"], {})

    authenticator = factory.create_component(
        model_type=OAuthAuthenticatorModel, component_definition=authenticator_config, config=input_config
    )

    assert isinstance(authenticator, DeclarativeOauth2Authenticator)
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
      type: ListStreamSlicer
      slice_values: "*ref(repositories)"
      cursor_field: repository
    """
    parsed_manifest = YamlDeclarativeSource._parse(content)
    resolved_manifest = resolver.preprocess_manifest(parsed_manifest, {}, "")
    slicer_config = transformer.propagate_types_and_options("", resolved_manifest["stream_slicer"], {})

    stream_slicer = factory.create_component(model_type=ListStreamSlicerModel, component_definition=slicer_config, config=input_config)

    assert isinstance(stream_slicer, ListStreamSlicer)
    assert stream_slicer.slice_values == ["airbyte", "airbyte-cloud"]


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
    parsed_manifest = YamlDeclarativeSource._parse(content)
    resolved_manifest = resolver.preprocess_manifest(parsed_manifest, {}, "")
    slicer_config = transformer.propagate_types_and_options("", resolved_manifest["stream_slicer"], {})

    stream_slicer = factory.create_component(model_type=ListStreamSlicerModel, component_definition=slicer_config, config=input_config)

    assert isinstance(stream_slicer, ListStreamSlicer)
    assert stream_slicer.slice_values == ["airbyte", "airbyte-cloud"]
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
    parsed_manifest = YamlDeclarativeSource._parse(content)
    resolved_manifest = resolver.preprocess_manifest(parsed_manifest, {}, "")
    slicer_config = transformer.propagate_types_and_options("", resolved_manifest["stream_slicer"], {})

    stream_slicer = factory.create_component(model_type=SubstreamSlicerModel, component_definition=slicer_config, config=input_config)

    assert isinstance(stream_slicer, SubstreamSlicer)
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
    parsed_manifest = YamlDeclarativeSource._parse(content)
    resolved_manifest = resolver.preprocess_manifest(parsed_manifest, {}, "")
    slicer_config = transformer.propagate_types_and_options("", resolved_manifest["stream_slicer"], {})

    stream_slicer = factory.create_component(
        model_type=CartesianProductStreamSlicerModel, component_definition=slicer_config, config=input_config
    )

    assert isinstance(stream_slicer, CartesianProductStreamSlicer)
    underlying_slicers = stream_slicer.stream_slicers
    assert len(stream_slicer.stream_slicers) == 2

    underlying_slicer_0 = underlying_slicers[0]
    assert isinstance(underlying_slicer_0, ListStreamSlicer)
    assert ["airbyte", "airbyte-cloud"] == underlying_slicer_0.slice_values

    underlying_slicer_1 = underlying_slicers[1]
    assert isinstance(underlying_slicer_1, ListStreamSlicer)
    assert ["hello", "world"] == underlying_slicer_1.slice_values


def test_datetime_stream_slicer():
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
        step: "10d"
        cursor_field: "created"
        lookback_window: "5d"
        start_time_option:
          inject_into: request_parameter
          field_name: created[gte]
        end_time_option:
          inject_into: body_json
          field_name: end_time
        stream_state_field_start: star
        stream_state_field_end: en
    """
    parsed_manifest = YamlDeclarativeSource._parse(content)
    resolved_manifest = resolver.preprocess_manifest(parsed_manifest, {}, "")
    slicer_config = transformer.propagate_types_and_options("", resolved_manifest["stream_slicer"], {})

    stream_slicer = factory.create_component(model_type=DatetimeStreamSlicerModel, component_definition=slicer_config, config=input_config)

    assert isinstance(stream_slicer, DatetimeStreamSlicer)
    assert stream_slicer._timezone == datetime.timezone.utc
    assert stream_slicer._step == relativedelta(days=10)
    assert stream_slicer.cursor_field.string == "created"
    assert stream_slicer.lookback_window.string == "5d"
    assert stream_slicer.start_time_option.inject_into == RequestOptionType.request_parameter
    assert stream_slicer.start_time_option.field_name == "created[gte]"
    assert stream_slicer.end_time_option.inject_into == RequestOptionType.body_json
    assert stream_slicer.end_time_option.field_name == "end_time"
    assert stream_slicer.stream_state_field_start == "star"
    assert stream_slicer.stream_state_field_end == "en"

    assert isinstance(stream_slicer.start_datetime, MinMaxDatetime)
    assert stream_slicer.start_datetime._datetime_format == "%Y-%m-%dT%H:%M:%S.%f%z"
    assert stream_slicer.start_datetime._timezone == datetime.timezone.utc
    assert stream_slicer.start_datetime.datetime.string == "{{ config['start_time'] }}"
    assert stream_slicer.start_datetime.min_datetime.string == "{{ config['start_time'] + day_delta(2) }}"

    assert isinstance(stream_slicer.end_datetime, MinMaxDatetime)
    assert stream_slicer.end_datetime.datetime.string == "{{ config['end_time'] }}"


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
      type: RecordSelector
      record_filter:
        type: RecordFilter
        condition: "{{{{ record['id'] > stream_state['id'] }}}}"
      extractor:
        $ref: "*ref(extractor)"
        field_pointer: ["{record_selector}"]
    """
    parsed_manifest = YamlDeclarativeSource._parse(content)
    resolved_manifest = resolver.preprocess_manifest(parsed_manifest, {}, "")
    selector_config = transformer.propagate_types_and_options("", resolved_manifest["selector"], {})

    selector = factory.create_component(model_type=RecordSelectorModel, component_definition=selector_config, config=input_config)

    assert isinstance(selector, RecordSelector)
    assert isinstance(selector.extractor, DpathExtractor)
    assert [fp.eval(input_config) for fp in selector.extractor.field_pointer] == [expected_runtime_selector]
    assert isinstance(selector.record_filter, RecordFilter)
    assert selector.record_filter.condition == "{{ record['id'] > stream_state['id'] }}"


@pytest.mark.parametrize(
    "test_name, error_handler, expected_backoff_strategy_type",
    [
        (
            "test_create_requester_constant_error_handler",
            """
  error_handler:
    backoff_strategies:
      - type: "ConstantBackoffStrategy"
        backoff_time_in_seconds: 5
            """,
            ConstantBackoffStrategy,
        ),
        (
            "test_create_requester_exponential_error_handler",
            """
  error_handler:
    backoff_strategies:
      - type: "ExponentialBackoffStrategy"
        factor: 5
            """,
            ExponentialBackoffStrategy,
        ),
        (
            "test_create_requester_wait_time_from_header_error_handler",
            """
  error_handler:
    backoff_strategies:
      - type: "WaitTimeFromHeader"
        header: "a_header"
            """,
            WaitTimeFromHeaderBackoffStrategy,
        ),
        (
            "test_create_requester_wait_time_until_from_header_error_handler",
            """
  error_handler:
    backoff_strategies:
      - type: "WaitUntilTimeFromHeader"
        header: "a_header"
            """,
            WaitUntilTimeFromHeaderBackoffStrategy,
        ),
        ("test_create_requester_no_error_handler", """""", ExponentialBackoffStrategy),
    ],
)
def test_create_requester(test_name, error_handler, expected_backoff_strategy_type):
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
    parsed_manifest = YamlDeclarativeSource._parse(content)
    resolved_manifest = resolver.preprocess_manifest(parsed_manifest, {}, "")
    requester_config = transformer.propagate_types_and_options("", resolved_manifest["requester"], {})

    selector = factory.create_component(model_type=HttpRequesterModel, component_definition=requester_config, config=input_config)

    assert isinstance(selector, HttpRequester)
    assert selector._method == HttpMethod.GET
    assert selector.name == "lists"
    assert selector.path.string == "/v3/marketing/lists"
    assert selector.url_base.string == "https://api.sendgrid.com"

    assert isinstance(selector.error_handler, DefaultErrorHandler)
    assert len(selector.error_handler.backoff_strategies) == 1
    assert isinstance(selector.error_handler.backoff_strategies[0], expected_backoff_strategy_type)

    assert isinstance(selector.authenticator, BasicHttpAuthenticator)
    assert selector.authenticator._username.eval(input_config) == "lists"
    assert selector.authenticator._password.eval(input_config) == "verysecrettoken"

    assert isinstance(selector._request_options_provider, InterpolatedRequestOptionsProvider)
    assert selector._request_options_provider._parameter_interpolator._interpolator.mapping["a_parameter"] == "something_here"
    assert selector._request_options_provider._headers_interpolator._interpolator.mapping["header"] == "header_value"


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
    parsed_manifest = YamlDeclarativeSource._parse(content)
    resolved_manifest = resolver.preprocess_manifest(parsed_manifest, {}, "")
    error_handler_config = transformer.propagate_types_and_options("", resolved_manifest["error_handler"], {})

    error_handler = factory.create_component(
        model_type=CompositeErrorHandlerModel, component_definition=error_handler_config, config=input_config
    )

    assert isinstance(error_handler, CompositeErrorHandler)
    assert len(error_handler.error_handlers) == 2

    error_handler_0 = error_handler.error_handlers[0]
    assert isinstance(error_handler_0, DefaultErrorHandler)
    assert isinstance(error_handler_0.response_filters[0], HttpResponseFilter)
    assert error_handler_0.response_filters[0].predicate.condition == "{{ 'code' in response }}"
    assert error_handler_0.response_filters[0].action == ResponseAction.RETRY

    error_handler_1 = error_handler.error_handlers[1]
    assert isinstance(error_handler_1, DefaultErrorHandler)
    assert isinstance(error_handler_1.response_filters[0], HttpResponseFilter)
    assert error_handler_1.response_filters[0].http_codes == {403}
    assert error_handler_1.response_filters[0].action == ResponseAction.RETRY


# This might be a better test for the manifest transformer but also worth testing end-to-end here as well
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
    parsed_manifest = YamlDeclarativeSource._parse(content)
    resolved_manifest = resolver.preprocess_manifest(parsed_manifest, {}, "")
    resolved_manifest["type"] = "DeclarativeSource"
    stream_config = transformer.propagate_types_and_options("", resolved_manifest["lists_stream"], {})

    stream = factory.create_component(model_type=DeclarativeStreamModel, component_definition=stream_config, config=input_config)

    assert isinstance(stream, DeclarativeStream)
    assert stream.primary_key == "id"
    assert stream.name == "lists"
    assert isinstance(stream.retriever, SimpleRetriever)

    assert isinstance(stream.schema_loader, JsonFileSchemaLoader)
    assert stream.schema_loader.file_path.string == "./source_sendgrid/schemas/{{ options.name }}.yaml"
    assert stream.schema_loader.file_path.default == "./source_sendgrid/schemas/{{ options.name }}.yaml"

    assert isinstance(stream.retriever.requester, HttpRequester)
    assert stream.retriever.requester.http_method == HttpMethod.GET

    assert isinstance(stream.retriever.requester.authenticator, BearerAuthenticator)
    assert stream.retriever.requester.authenticator._token.eval(input_config) == "verysecrettoken"

    assert isinstance(stream.retriever.record_selector, RecordSelector)
    assert isinstance(stream.retriever.record_selector.extractor, DpathExtractor)
    assert [fp.eval(input_config) for fp in stream.retriever.record_selector.extractor.field_pointer] == ["result"]

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
    parsed_manifest = YamlDeclarativeSource._parse(content)
    resolved_manifest = resolver.preprocess_manifest(parsed_manifest, {}, "")
    paginator_config = transformer.propagate_types_and_options("", resolved_manifest["paginator"], {})

    paginator = factory.create_component(model_type=DefaultPaginatorModel, component_definition=paginator_config, config=input_config)

    assert isinstance(paginator, DefaultPaginator)
    assert paginator.url_base.string == "https://airbyte.io"

    assert isinstance(paginator.pagination_strategy, CursorPaginationStrategy)
    assert paginator.pagination_strategy.page_size == 50
    assert paginator.pagination_strategy.cursor_value.string == "{{ response._metadata.next }}"

    assert isinstance(paginator.page_size_option, RequestOption)
    assert paginator.page_size_option.inject_into == RequestOptionType.request_parameter
    assert paginator.page_size_option.field_name == "page_size"

    assert isinstance(paginator.page_token_option, RequestOption)
    assert paginator.page_token_option.inject_into == RequestOptionType.path


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
        parsed_manifest = YamlDeclarativeSource._parse(content)
        resolved_manifest = resolver.preprocess_manifest(parsed_manifest, {}, "")
        resolved_manifest["type"] = "DeclarativeSource"
        stream_config = transformer.propagate_types_and_options("", resolved_manifest["the_stream"], {})

        stream = factory.create_component(model_type=DeclarativeStreamModel, component_definition=stream_config, config=input_config)

        assert isinstance(stream, DeclarativeStream)
        assert [] == stream.transformations

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
        parsed_manifest = YamlDeclarativeSource._parse(content)
        resolved_manifest = resolver.preprocess_manifest(parsed_manifest, {}, "")
        resolved_manifest["type"] = "DeclarativeSource"
        stream_config = transformer.propagate_types_and_options("", resolved_manifest["the_stream"], {})

        stream = factory.create_component(model_type=DeclarativeStreamModel, component_definition=stream_config, config=input_config)

        assert isinstance(stream, DeclarativeStream)
        expected = [RemoveFields(field_pointers=[["path", "to", "field1"], ["path2"]], options={})]
        assert stream.transformations == expected

    def test_add_fields(self):
        content = f"""
        the_stream:
            type: DeclarativeStream
            $options:
                {self.base_options}
                transformations:
                    - type: AddFields
                      fields:
                        - path: ["field1"]
                          value: "static_value"
        """
        parsed_manifest = YamlDeclarativeSource._parse(content)
        resolved_manifest = resolver.preprocess_manifest(parsed_manifest, {}, "")
        resolved_manifest["type"] = "DeclarativeSource"
        stream_config = transformer.propagate_types_and_options("", resolved_manifest["the_stream"], {})

        stream = factory.create_component(model_type=DeclarativeStreamModel, component_definition=stream_config, config=input_config)

        assert isinstance(stream, DeclarativeStream)
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
        assert stream.transformations == expected
