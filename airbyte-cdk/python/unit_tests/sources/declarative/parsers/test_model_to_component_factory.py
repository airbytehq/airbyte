#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

# mypy: ignore-errors

import datetime

import pytest
from airbyte_cdk.models import Level
from airbyte_cdk.sources.declarative.auth import DeclarativeOauth2Authenticator
from airbyte_cdk.sources.declarative.auth.token import BasicHttpAuthenticator, BearerAuthenticator, SessionTokenAuthenticator
from airbyte_cdk.sources.declarative.checks import CheckStream
from airbyte_cdk.sources.declarative.datetime import MinMaxDatetime
from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream
from airbyte_cdk.sources.declarative.decoders import JsonDecoder
from airbyte_cdk.sources.declarative.extractors import DpathExtractor, RecordFilter, RecordSelector
from airbyte_cdk.sources.declarative.incremental import DatetimeBasedCursor, PerPartitionCursor
from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.models import CheckStream as CheckStreamModel
from airbyte_cdk.sources.declarative.models import CompositeErrorHandler as CompositeErrorHandlerModel
from airbyte_cdk.sources.declarative.models import CustomErrorHandler as CustomErrorHandlerModel
from airbyte_cdk.sources.declarative.models import CustomPartitionRouter as CustomPartitionRouterModel
from airbyte_cdk.sources.declarative.models import DatetimeBasedCursor as DatetimeBasedCursorModel
from airbyte_cdk.sources.declarative.models import DeclarativeStream as DeclarativeStreamModel
from airbyte_cdk.sources.declarative.models import DefaultPaginator as DefaultPaginatorModel
from airbyte_cdk.sources.declarative.models import HttpRequester as HttpRequesterModel
from airbyte_cdk.sources.declarative.models import ListPartitionRouter as ListPartitionRouterModel
from airbyte_cdk.sources.declarative.models import OAuthAuthenticator as OAuthAuthenticatorModel
from airbyte_cdk.sources.declarative.models import RecordSelector as RecordSelectorModel
from airbyte_cdk.sources.declarative.models import SimpleRetriever as SimpleRetrieverModel
from airbyte_cdk.sources.declarative.models import Spec as SpecModel
from airbyte_cdk.sources.declarative.models import SubstreamPartitionRouter as SubstreamPartitionRouterModel
from airbyte_cdk.sources.declarative.parsers.manifest_component_transformer import ManifestComponentTransformer
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.declarative.partition_routers import ListPartitionRouter, SinglePartitionRouter, SubstreamPartitionRouter
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
from airbyte_cdk.sources.declarative.requesters.paginators.strategies import (
    CursorPaginationStrategy,
    OffsetIncrement,
    PageIncrement,
    StopConditionPaginationStrategyDecorator,
)
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption, RequestOptionType
from airbyte_cdk.sources.declarative.requesters.request_options import InterpolatedRequestOptionsProvider
from airbyte_cdk.sources.declarative.requesters.request_path import RequestPath
from airbyte_cdk.sources.declarative.requesters.requester import HttpMethod
from airbyte_cdk.sources.declarative.retrievers import SimpleRetriever, SimpleRetrieverTestReadDecorator
from airbyte_cdk.sources.declarative.schema import JsonFileSchemaLoader
from airbyte_cdk.sources.declarative.spec import Spec
from airbyte_cdk.sources.declarative.stream_slicers import CartesianProductStreamSlicer
from airbyte_cdk.sources.declarative.transformations import AddFields, RemoveFields
from airbyte_cdk.sources.declarative.transformations.add_fields import AddedFieldDefinition
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.streams.http.requests_native_auth.oauth import SingleUseRefreshTokenOauth2Authenticator
from unit_tests.sources.declarative.parsers.testing_components import TestingCustomSubstreamPartitionRouter, TestingSomeComponent

factory = ModelToComponentFactory()

resolver = ManifestReferenceResolver()

transformer = ManifestComponentTransformer()

input_config = {"apikey": "verysecrettoken", "repos": ["airbyte", "airbyte-cloud"]}


def test_create_check_stream():
    manifest = {"check": {"type": "CheckStream", "stream_names": ["list_stream"]}}

    check = factory.create_component(CheckStreamModel, manifest["check"], {})

    assert isinstance(check, CheckStream)
    assert check.stream_names == ["list_stream"]


def test_create_component_type_mismatch():
    manifest = {"check": {"type": "MismatchType", "stream_names": ["list_stream"]}}

    with pytest.raises(ValueError):
        factory.create_component(CheckStreamModel, manifest["check"], {})


def test_full_config_stream():
    content = """
decoder:
  type: JsonDecoder
extractor:
  type: DpathExtractor
  decoder: "#/decoder"
selector:
  type: RecordSelector
  record_filter:
    type: RecordFilter
    condition: "{{ record['id'] > stream_state['id'] }}"
metadata_paginator:
    type: DefaultPaginator
    page_size_option:
      type: RequestOption
      inject_into: request_parameter
      field_name: page_size
    page_token_option:
      type: RequestPath
    pagination_strategy:
      type: "CursorPagination"
      cursor_value: "{{ response._metadata.next }}"
      page_size: 10
requester:
  type: HttpRequester
  url_base: "https://api.sendgrid.com/v3/"
  http_method: "GET"
  authenticator:
    type: BearerAuthenticator
    api_token: "{{ config['apikey'] }}"
  request_parameters:
    unit: "day"
retriever:
  paginator:
    type: NoPagination
partial_stream:
  type: DeclarativeStream
  schema_loader:
    type: JsonFileSchemaLoader
    file_path: "./source_sendgrid/schemas/{{ parameters.name }}.json"
list_stream:
  $ref: "#/partial_stream"
  $parameters:
    name: "lists"
    extractor:
      $ref: "#/extractor"
      field_path: ["{{ parameters['name'] }}"]
  name: "lists"
  primary_key: "id"
  retriever:
    $ref: "#/retriever"
    requester:
      $ref: "#/requester"
      path: "{{ next_page_token['next_page_url'] }}"
    paginator:
      $ref: "#/metadata_paginator"
    record_selector:
      $ref: "#/selector"
  transformations:
    - type: AddFields
      fields:
      - path: ["extra"]
        value: "{{ response.to_add }}"
  incremental_sync:
    type: DatetimeBasedCursor
    start_datetime: "{{ config['start_time'] }}"
    end_datetime: "{{ config['end_time'] }}"
    step: "P10D"
    cursor_field: "created"
    cursor_granularity: "PT0.000001S"
    $parameters:
      datetime_format: "%Y-%m-%dT%H:%M:%S.%f%z"
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
  advanced_auth:
    auth_flow_type: "oauth2.0"
    """
    parsed_manifest = YamlDeclarativeSource._parse(content)
    resolved_manifest = resolver.preprocess_manifest(parsed_manifest)
    resolved_manifest["type"] = "DeclarativeSource"
    manifest = transformer.propagate_types_and_parameters("", resolved_manifest, {})

    stream_manifest = manifest["list_stream"]
    assert stream_manifest["type"] == "DeclarativeStream"
    stream = factory.create_component(model_type=DeclarativeStreamModel, component_definition=stream_manifest, config=input_config)

    assert isinstance(stream, DeclarativeStream)
    assert stream.primary_key == "id"
    assert stream.name == "lists"
    assert stream.stream_cursor_field.string == "created"

    assert isinstance(stream.schema_loader, JsonFileSchemaLoader)
    assert stream.schema_loader._get_json_filepath() == "./source_sendgrid/schemas/lists.json"

    assert len(stream.retriever.record_selector.transformations) == 1
    add_fields = stream.retriever.record_selector.transformations[0]
    assert isinstance(add_fields, AddFields)
    assert add_fields.fields[0].path == ["extra"]
    assert add_fields.fields[0].value.string == "{{ response.to_add }}"

    assert isinstance(stream.retriever, SimpleRetriever)
    assert stream.retriever.primary_key == stream.primary_key
    assert stream.retriever.name == stream.name

    assert isinstance(stream.retriever.record_selector, RecordSelector)

    assert isinstance(stream.retriever.record_selector.extractor, DpathExtractor)
    assert isinstance(stream.retriever.record_selector.extractor.decoder, JsonDecoder)
    assert [fp.eval(input_config) for fp in stream.retriever.record_selector.extractor.field_path] == ["lists"]

    assert isinstance(stream.retriever.record_selector.record_filter, RecordFilter)
    assert stream.retriever.record_selector.record_filter._filter_interpolator.condition == "{{ record['id'] > stream_state['id'] }}"

    assert isinstance(stream.retriever.paginator, DefaultPaginator)
    assert isinstance(stream.retriever.paginator.decoder, JsonDecoder)
    assert stream.retriever.paginator.page_size_option.field_name == "page_size"
    assert stream.retriever.paginator.page_size_option.inject_into == RequestOptionType.request_parameter
    assert isinstance(stream.retriever.paginator.page_token_option, RequestPath)
    assert stream.retriever.paginator.url_base.string == "https://api.sendgrid.com/v3/"
    assert stream.retriever.paginator.url_base.default == "https://api.sendgrid.com/v3/"

    assert isinstance(stream.retriever.paginator.pagination_strategy, CursorPaginationStrategy)
    assert isinstance(stream.retriever.paginator.pagination_strategy.decoder, JsonDecoder)
    assert stream.retriever.paginator.pagination_strategy.cursor_value.string == "{{ response._metadata.next }}"
    assert stream.retriever.paginator.pagination_strategy.cursor_value.default == "{{ response._metadata.next }}"
    assert stream.retriever.paginator.pagination_strategy.page_size == 10

    assert isinstance(stream.retriever.requester, HttpRequester)
    assert stream.retriever.requester.http_method == HttpMethod.GET
    assert stream.retriever.requester.name == stream.name
    assert stream.retriever.requester.path.string == "{{ next_page_token['next_page_url'] }}"
    assert stream.retriever.requester.path.default == "{{ next_page_token['next_page_url'] }}"

    assert isinstance(stream.retriever.requester.authenticator, BearerAuthenticator)
    assert stream.retriever.requester.authenticator._token.eval(input_config) == "verysecrettoken"

    assert isinstance(stream.retriever.requester.request_options_provider, InterpolatedRequestOptionsProvider)
    assert stream.retriever.requester.request_options_provider.request_parameters.get("unit") == "day"

    checker = factory.create_component(model_type=CheckStreamModel, component_definition=manifest["check"], config=input_config)

    assert isinstance(checker, CheckStream)
    streams_to_check = checker.stream_names
    assert len(streams_to_check) == 1
    assert list(streams_to_check)[0] == "list_stream"

    spec = factory.create_component(model_type=SpecModel, component_definition=manifest["spec"], config=input_config)

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
    advanced_auth = spec.advanced_auth
    assert advanced_auth.auth_flow_type.value == "oauth2.0"


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
    resolved_manifest = resolver.preprocess_manifest(parsed_manifest)
    authenticator_manifest = transformer.propagate_types_and_parameters("", resolved_manifest["authenticator"], {})

    authenticator = factory.create_component(
        model_type=OAuthAuthenticatorModel, component_definition=authenticator_manifest, config=input_config
    )

    assert isinstance(authenticator, DeclarativeOauth2Authenticator)
    assert authenticator.client_id.eval(input_config) == "some_client_id"
    assert authenticator.client_secret.string == "some_client_secret"
    assert authenticator.token_refresh_endpoint.eval(input_config) == "https://api.sendgrid.com/v3/auth"
    assert authenticator.refresh_token.eval(input_config) == "verysecrettoken"
    assert authenticator._refresh_request_body.mapping == {"body_field": "yoyoyo", "interpolated_body_field": "{{ config['apikey'] }}"}
    assert authenticator.get_refresh_request_body() == {"body_field": "yoyoyo", "interpolated_body_field": "verysecrettoken"}


def test_single_use_oauth_branch():
    single_use_input_config = {"apikey": "verysecrettoken", "repos": ["airbyte", "airbyte-cloud"], "credentials": {"access_token": "access_token", "token_expiry_date": "1970-01-01"}}

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
      refresh_token_updater:
        refresh_token_name: "the_refresh_token"
        refresh_token_config_path:
          - apikey
    """
    parsed_manifest = YamlDeclarativeSource._parse(content)
    resolved_manifest = resolver.preprocess_manifest(parsed_manifest)
    authenticator_manifest = transformer.propagate_types_and_parameters("", resolved_manifest["authenticator"], {})

    authenticator: SingleUseRefreshTokenOauth2Authenticator = factory.create_component(
        model_type=OAuthAuthenticatorModel, component_definition=authenticator_manifest, config=single_use_input_config
    )

    assert isinstance(authenticator, SingleUseRefreshTokenOauth2Authenticator)
    assert authenticator._client_id == "some_client_id"
    assert authenticator._client_secret == "some_client_secret"
    assert authenticator._token_refresh_endpoint == "https://api.sendgrid.com/v3/auth"
    assert authenticator._refresh_token == "verysecrettoken"
    assert authenticator._refresh_request_body == {"body_field": "yoyoyo", "interpolated_body_field": "verysecrettoken"}
    assert authenticator._refresh_token_name == "the_refresh_token"
    assert authenticator._refresh_token_config_path == ["apikey"]
    # default values
    assert authenticator._access_token_config_path == ["credentials", "access_token"]
    assert authenticator._token_expiry_date_config_path == ["credentials", "token_expiry_date"]


def test_list_based_stream_slicer_with_values_refd():
    content = """
    repositories: ["airbyte", "airbyte-cloud"]
    partition_router:
      type: ListPartitionRouter
      values: "#/repositories"
      cursor_field: repository
    """
    parsed_manifest = YamlDeclarativeSource._parse(content)
    resolved_manifest = resolver.preprocess_manifest(parsed_manifest)
    partition_router_manifest = transformer.propagate_types_and_parameters("", resolved_manifest["partition_router"], {})

    partition_router = factory.create_component(
        model_type=ListPartitionRouterModel, component_definition=partition_router_manifest, config=input_config
    )

    assert isinstance(partition_router, ListPartitionRouter)
    assert partition_router.values == ["airbyte", "airbyte-cloud"]


def test_list_based_stream_slicer_with_values_defined_in_config():
    content = """
    partition_router:
      type: ListPartitionRouter
      values: "{{config['repos']}}"
      cursor_field: repository
      request_option:
        type: RequestOption
        inject_into: header
        field_name: repository
    """
    parsed_manifest = YamlDeclarativeSource._parse(content)
    resolved_manifest = resolver.preprocess_manifest(parsed_manifest)
    partition_router_manifest = transformer.propagate_types_and_parameters("", resolved_manifest["partition_router"], {})

    partition_router = factory.create_component(
        model_type=ListPartitionRouterModel, component_definition=partition_router_manifest, config=input_config
    )

    assert isinstance(partition_router, ListPartitionRouter)
    assert partition_router.values == ["airbyte", "airbyte-cloud"]
    assert partition_router.request_option.inject_into == RequestOptionType.header
    assert partition_router.request_option.field_name == "repository"


def test_create_substream_partition_router():
    content = """
    schema_loader:
      file_path: "./source_sendgrid/schemas/{{ parameters['name'] }}.yaml"
      name: "{{ parameters['stream_name'] }}"
    retriever:
      requester:
        type: "HttpRequester"
        path: "kek"
      record_selector:
        extractor:
          field_path: []
    stream_A:
      type: DeclarativeStream
      name: "A"
      primary_key: "id"
      $parameters:
        retriever: "#/retriever"
        url_base: "https://airbyte.io"
        schema_loader: "#/schema_loader"
    stream_B:
      type: DeclarativeStream
      name: "B"
      primary_key: "id"
      $parameters:
        retriever: "#/retriever"
        url_base: "https://airbyte.io"
        schema_loader: "#/schema_loader"
    partition_router:
      type: SubstreamPartitionRouter
      parent_stream_configs:
        - stream: "#/stream_A"
          parent_key: id
          partition_field: repository_id
          request_option:
            type: RequestOption
            inject_into: request_parameter
            field_name: repository_id
        - stream: "#/stream_B"
          parent_key: someid
          partition_field: word_id
    """
    parsed_manifest = YamlDeclarativeSource._parse(content)
    resolved_manifest = resolver.preprocess_manifest(parsed_manifest)
    partition_router_manifest = transformer.propagate_types_and_parameters("", resolved_manifest["partition_router"], {})

    partition_router = factory.create_component(
        model_type=SubstreamPartitionRouterModel, component_definition=partition_router_manifest, config=input_config
    )

    assert isinstance(partition_router, SubstreamPartitionRouter)
    parent_stream_configs = partition_router.parent_stream_configs
    assert len(parent_stream_configs) == 2
    assert isinstance(parent_stream_configs[0].stream, DeclarativeStream)
    assert isinstance(parent_stream_configs[1].stream, DeclarativeStream)

    assert partition_router.parent_stream_configs[0].parent_key.eval({}) == "id"
    assert partition_router.parent_stream_configs[0].partition_field.eval({}) == "repository_id"
    assert partition_router.parent_stream_configs[0].request_option.inject_into == RequestOptionType.request_parameter
    assert partition_router.parent_stream_configs[0].request_option.field_name == "repository_id"

    assert partition_router.parent_stream_configs[1].parent_key.eval({}) == "someid"
    assert partition_router.parent_stream_configs[1].partition_field.eval({}) == "word_id"
    assert partition_router.parent_stream_configs[1].request_option is None


def test_datetime_based_cursor():
    content = """
    incremental:
        type: DatetimeBasedCursor
        $parameters:
          datetime_format: "%Y-%m-%dT%H:%M:%S.%f%z"
        start_datetime:
          type: MinMaxDatetime
          datetime: "{{ config['start_time'] }}"
          min_datetime: "{{ config['start_time'] + day_delta(2) }}"
        end_datetime: "{{ config['end_time'] }}"
        step: "P10D"
        cursor_field: "created"
        cursor_granularity: "PT0.000001S"
        lookback_window: "P5D"
        start_time_option:
          type: RequestOption
          inject_into: request_parameter
          field_name: created[gte]
        end_time_option:
          type: RequestOption
          inject_into: body_json
          field_name: end_time
        partition_field_start: star
        partition_field_end: en
    """
    parsed_manifest = YamlDeclarativeSource._parse(content)
    resolved_manifest = resolver.preprocess_manifest(parsed_manifest)
    slicer_manifest = transformer.propagate_types_and_parameters("", resolved_manifest["incremental"], {})

    stream_slicer = factory.create_component(model_type=DatetimeBasedCursorModel, component_definition=slicer_manifest, config=input_config)

    assert isinstance(stream_slicer, DatetimeBasedCursor)
    assert stream_slicer._step == datetime.timedelta(days=10)
    assert stream_slicer.cursor_field.string == "created"
    assert stream_slicer.cursor_granularity == "PT0.000001S"
    assert stream_slicer.lookback_window.string == "P5D"
    assert stream_slicer.start_time_option.inject_into == RequestOptionType.request_parameter
    assert stream_slicer.start_time_option.field_name == "created[gte]"
    assert stream_slicer.end_time_option.inject_into == RequestOptionType.body_json
    assert stream_slicer.end_time_option.field_name == "end_time"
    assert stream_slicer.partition_field_start.eval({}) == "star"
    assert stream_slicer.partition_field_end.eval({}) == "en"

    assert isinstance(stream_slicer.start_datetime, MinMaxDatetime)
    assert stream_slicer.start_datetime._datetime_format == "%Y-%m-%dT%H:%M:%S.%f%z"
    assert stream_slicer.start_datetime.datetime.string == "{{ config['start_time'] }}"
    assert stream_slicer.start_datetime.min_datetime.string == "{{ config['start_time'] + day_delta(2) }}"

    assert isinstance(stream_slicer.end_datetime, MinMaxDatetime)
    assert stream_slicer.end_datetime.datetime.string == "{{ config['end_time'] }}"


def test_stream_with_incremental_and_retriever_with_partition_router():
    content = """
decoder:
  type: JsonDecoder
extractor:
  type: DpathExtractor
  decoder: "#/decoder"
selector:
  type: RecordSelector
  record_filter:
    type: RecordFilter
    condition: "{{ record['id'] > stream_state['id'] }}"
requester:
  type: HttpRequester
  name: "{{ parameters['name'] }}"
  url_base: "https://api.sendgrid.com/v3/"
  http_method: "GET"
  authenticator:
    type: BearerAuthenticator
    api_token: "{{ config['apikey'] }}"
  request_parameters:
    unit: "day"
list_stream:
  type: DeclarativeStream
  schema_loader:
    type: JsonFileSchemaLoader
    file_path: "./source_sendgrid/schemas/{{ parameters.name }}.json"
  incremental_sync:
    type: DatetimeBasedCursor
    $parameters:
      datetime_format: "%Y-%m-%dT%H:%M:%S.%f%z"
    start_datetime: "{{ config['start_time'] }}"
    end_datetime: "{{ config['end_time'] }}"
    step: "P10D"
    cursor_field: "created"
    cursor_granularity: "PT0.000001S"
    lookback_window: "P5D"
    start_time_option:
      inject_into: request_parameter
      field_name: created[gte]
    end_time_option:
      inject_into: body_json
      field_name: end_time
    partition_field_start: star
    partition_field_end: en
  retriever:
    type: SimpleRetriever
    name: "{{ parameters['name'] }}"
    partition_router:
      type: ListPartitionRouter
      values: "{{config['repos']}}"
      cursor_field: a_key
      request_option:
        inject_into: header
        field_name: a_key
    paginator:
      type: DefaultPaginator
      page_size_option:
        inject_into: request_parameter
        field_name: page_size
      page_token_option:
        inject_into: path
        type: RequestPath
      pagination_strategy:
        type: "CursorPagination"
        cursor_value: "{{ response._metadata.next }}"
        page_size: 10
    requester:
      $ref: "#/requester"
      path: "{{ next_page_token['next_page_url'] }}"
    record_selector:
      $ref: "#/selector"
  $parameters:
    name: "lists"
    primary_key: "id"
    extractor:
      $ref: "#/extractor"
      field_path: ["{{ parameters['name'] }}"]
    """

    parsed_manifest = YamlDeclarativeSource._parse(content)
    resolved_manifest = resolver.preprocess_manifest(parsed_manifest)
    stream_manifest = transformer.propagate_types_and_parameters("", resolved_manifest["list_stream"], {})

    stream = factory.create_component(model_type=DeclarativeStreamModel, component_definition=stream_manifest, config=input_config)

    assert isinstance(stream, DeclarativeStream)
    assert isinstance(stream.retriever, SimpleRetriever)
    assert isinstance(stream.retriever.stream_slicer, PerPartitionCursor)

    datetime_stream_slicer = stream.retriever.stream_slicer._cursor_factory.create()
    assert isinstance(datetime_stream_slicer, DatetimeBasedCursor)
    assert isinstance(datetime_stream_slicer.start_datetime, MinMaxDatetime)
    assert datetime_stream_slicer.start_datetime.datetime.string == "{{ config['start_time'] }}"
    assert isinstance(datetime_stream_slicer.end_datetime, MinMaxDatetime)
    assert datetime_stream_slicer.end_datetime.datetime.string == "{{ config['end_time'] }}"
    assert datetime_stream_slicer.step == "P10D"
    assert datetime_stream_slicer.cursor_field.string == "created"

    list_stream_slicer = stream.retriever.stream_slicer._partition_router
    assert isinstance(list_stream_slicer, ListPartitionRouter)
    assert list_stream_slicer.values == ["airbyte", "airbyte-cloud"]
    assert list_stream_slicer.cursor_field.string == "a_key"


def test_incremental_data_feed():
    content = """
selector:
  type: RecordSelector
  extractor:
      type: DpathExtractor
      field_path: ["extractor_path"]
  record_filter:
    type: RecordFilter
    condition: "{{ record['id'] > stream_state['id'] }}"
requester:
  type: HttpRequester
  name: "{{ parameters['name'] }}"
  url_base: "https://api.sendgrid.com/v3/"
  http_method: "GET"
list_stream:
  type: DeclarativeStream
  incremental_sync:
    type: DatetimeBasedCursor
    $parameters:
      datetime_format: "%Y-%m-%dT%H:%M:%S.%f%z"
    start_datetime: "{{ config['start_time'] }}"
    cursor_field: "created"
    is_data_feed: true
  retriever:
    type: SimpleRetriever
    name: "{{ parameters['name'] }}"
    paginator:
      type: DefaultPaginator
      pagination_strategy:
        type: "CursorPagination"
        cursor_value: "{{ response._metadata.next }}"
        page_size: 10
    requester:
      $ref: "#/requester"
      path: "/"
    record_selector:
      $ref: "#/selector"
  $parameters:
    name: "lists"
    """

    parsed_manifest = YamlDeclarativeSource._parse(content)
    resolved_manifest = resolver.preprocess_manifest(parsed_manifest)
    stream_manifest = transformer.propagate_types_and_parameters("", resolved_manifest["list_stream"], {})

    stream = factory.create_component(model_type=DeclarativeStreamModel, component_definition=stream_manifest, config=input_config)

    assert isinstance(stream.retriever.paginator.pagination_strategy, StopConditionPaginationStrategyDecorator)


def test_given_data_feed_and_incremental_then_raise_error():
    content = """
incremental_sync:
  type: DatetimeBasedCursor
  $parameters:
    datetime_format: "%Y-%m-%dT%H:%M:%S.%f%z"
  start_datetime: "{{ config['start_time'] }}"
  end_datetime: "2023-01-01"
  cursor_field: "created"
  is_data_feed: true"""

    parsed_incremental_sync = YamlDeclarativeSource._parse(content)
    resolved_incremental_sync = resolver.preprocess_manifest(parsed_incremental_sync)
    datetime_based_cursor_definition = transformer.propagate_types_and_parameters("", resolved_incremental_sync["incremental_sync"], {})

    with pytest.raises(ValueError):
        factory.create_component(
            model_type=DatetimeBasedCursorModel,
            component_definition=datetime_based_cursor_definition,
            config=input_config
        )


@pytest.mark.parametrize(
    "test_name, record_selector, expected_runtime_selector",
    [("test_static_record_selector", "result", "result"), ("test_options_record_selector", "{{ parameters['name'] }}", "lists")],
)
def test_create_record_selector(test_name, record_selector, expected_runtime_selector):
    content = f"""
    extractor:
      type: DpathExtractor
    selector:
      $parameters:
        name: "lists"
      type: RecordSelector
      record_filter:
        type: RecordFilter
        condition: "{{{{ record['id'] > stream_state['id'] }}}}"
      extractor:
        $ref: "#/extractor"
        field_path: ["{record_selector}"]
    """
    parsed_manifest = YamlDeclarativeSource._parse(content)
    resolved_manifest = resolver.preprocess_manifest(parsed_manifest)
    selector_manifest = transformer.propagate_types_and_parameters("", resolved_manifest["selector"], {})

    selector = factory.create_component(model_type=RecordSelectorModel, component_definition=selector_manifest, transformations=[], config=input_config)

    assert isinstance(selector, RecordSelector)
    assert isinstance(selector.extractor, DpathExtractor)
    assert [fp.eval(input_config) for fp in selector.extractor.field_path] == [expected_runtime_selector]
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
  $parameters:
    name: 'lists'
  url_base: "https://api.sendgrid.com"
  authenticator:
    type: "BasicHttpAuthenticator"
    username: "{{{{ parameters.name}}}}"
    password: "{{{{ config.apikey }}}}"
  request_parameters:
    a_parameter: "something_here"
  request_headers:
    header: header_value
  {error_handler}
    """
    name = "name"
    parsed_manifest = YamlDeclarativeSource._parse(content)
    resolved_manifest = resolver.preprocess_manifest(parsed_manifest)
    requester_manifest = transformer.propagate_types_and_parameters("", resolved_manifest["requester"], {})

    selector = factory.create_component(
        model_type=HttpRequesterModel, component_definition=requester_manifest, config=input_config, name=name
    )

    assert isinstance(selector, HttpRequester)
    assert selector._method == HttpMethod.GET
    assert selector.name == "name"
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


def test_create_request_with_session_authenticator():
    content = """
requester:
  type: HttpRequester
  path: "/v3/marketing/lists"
  $parameters:
    name: 'lists'
  url_base: "https://api.sendgrid.com"
  authenticator:
    type: "SessionTokenAuthenticator"
    username: "{{ parameters.name}}"
    password: "{{ config.apikey }}"
    login_url: "login"
    header: "token"
    session_token_response_key: "session"
    validate_session_url: validate
  request_parameters:
    a_parameter: "something_here"
  request_headers:
    header: header_value
    """
    name = "name"
    parsed_manifest = YamlDeclarativeSource._parse(content)
    resolved_manifest = resolver.preprocess_manifest(parsed_manifest)
    requester_manifest = transformer.propagate_types_and_parameters("", resolved_manifest["requester"], {})

    selector = factory.create_component(
        model_type=HttpRequesterModel, component_definition=requester_manifest, config=input_config, name=name
    )

    assert isinstance(selector, HttpRequester)
    assert isinstance(selector.authenticator, SessionTokenAuthenticator)
    assert selector.authenticator._username.eval(input_config) == "lists"
    assert selector.authenticator._password.eval(input_config) == "verysecrettoken"
    assert selector.authenticator._api_url.eval(input_config) == "https://api.sendgrid.com"


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
    resolved_manifest = resolver.preprocess_manifest(parsed_manifest)
    error_handler_manifest = transformer.propagate_types_and_parameters("", resolved_manifest["error_handler"], {})

    error_handler = factory.create_component(
        model_type=CompositeErrorHandlerModel, component_definition=error_handler_manifest, config=input_config
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
      name: "lists"
      primary_key: id
      $parameters:
        name: "lists"
        url_base: "https://api.sendgrid.com"
        schema_loader:
          name: "{{ parameters.stream_name }}"
          file_path: "./source_sendgrid/schemas/{{ parameters.name }}.yaml"
        retriever:
          paginator:
            type: "DefaultPaginator"
            page_size_option:
              type: RequestOption
              inject_into: request_parameter
              field_name: page_size
            page_token_option:
              type: RequestPath
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
              field_path: ["result"]
    streams:
      - "#/lists_stream"
    """
    parsed_manifest = YamlDeclarativeSource._parse(content)
    resolved_manifest = resolver.preprocess_manifest(parsed_manifest)
    resolved_manifest["type"] = "DeclarativeSource"
    stream_manifest = transformer.propagate_types_and_parameters("", resolved_manifest["lists_stream"], {})

    stream = factory.create_component(model_type=DeclarativeStreamModel, component_definition=stream_manifest, config=input_config)

    assert isinstance(stream, DeclarativeStream)
    assert stream.primary_key == "id"
    assert stream.name == "lists"
    assert isinstance(stream.retriever, SimpleRetriever)
    assert stream.retriever.name == stream.name
    assert stream.retriever.primary_key == stream.primary_key

    assert isinstance(stream.schema_loader, JsonFileSchemaLoader)
    assert stream.schema_loader.file_path.string == "./source_sendgrid/schemas/{{ parameters.name }}.yaml"
    assert stream.schema_loader.file_path.default == "./source_sendgrid/schemas/{{ parameters.name }}.yaml"

    assert isinstance(stream.retriever.requester, HttpRequester)
    assert stream.retriever.requester.http_method == HttpMethod.GET

    assert isinstance(stream.retriever.requester.authenticator, BearerAuthenticator)
    assert stream.retriever.requester.authenticator._token.eval(input_config) == "verysecrettoken"

    assert isinstance(stream.retriever.record_selector, RecordSelector)
    assert isinstance(stream.retriever.record_selector.extractor, DpathExtractor)
    assert [fp.eval(input_config) for fp in stream.retriever.record_selector.extractor.field_path] == ["result"]

    assert isinstance(stream.retriever.paginator, DefaultPaginator)
    assert stream.retriever.paginator.url_base.string == "https://api.sendgrid.com"
    assert stream.retriever.paginator.pagination_strategy.get_page_size() == 10


def test_create_default_paginator():
    content = """
      paginator:
        type: "DefaultPaginator"
        page_size_option:
          type: RequestOption
          inject_into: request_parameter
          field_name: page_size
        page_token_option:
          type: RequestPath
        pagination_strategy:
          type: "CursorPagination"
          page_size: 50
          cursor_value: "{{ response._metadata.next }}"
    """
    parsed_manifest = YamlDeclarativeSource._parse(content)
    resolved_manifest = resolver.preprocess_manifest(parsed_manifest)
    paginator_manifest = transformer.propagate_types_and_parameters("", resolved_manifest["paginator"], {})

    paginator = factory.create_component(
        model_type=DefaultPaginatorModel, component_definition=paginator_manifest, config=input_config, url_base="https://airbyte.io"
    )

    assert isinstance(paginator, DefaultPaginator)
    assert paginator.url_base.string == "https://airbyte.io"

    assert isinstance(paginator.pagination_strategy, CursorPaginationStrategy)
    assert paginator.pagination_strategy.page_size == 50
    assert paginator.pagination_strategy.cursor_value.string == "{{ response._metadata.next }}"

    assert isinstance(paginator.page_size_option, RequestOption)
    assert paginator.page_size_option.inject_into == RequestOptionType.request_parameter
    assert paginator.page_size_option.field_name == "page_size"

    assert isinstance(paginator.page_token_option, RequestPath)


@pytest.mark.parametrize(
    "manifest, field_name, expected_value, expected_error",
    [
        pytest.param(
            {
                "type": "CustomErrorHandler",
                "class_name": "unit_tests.sources.declarative.parsers.testing_components.TestingSomeComponent",
                "subcomponent_field_with_hint": {"type": "DpathExtractor", "field_path": []},
            },
            "subcomponent_field_with_hint",
            DpathExtractor(field_path=[], config={"apikey": "verysecrettoken", "repos": ["airbyte", "airbyte-cloud"]}, parameters={}),
            None,
            id="test_create_custom_component_with_subcomponent_that_must_be_parsed",
        ),
        pytest.param(
            {
                "type": "CustomErrorHandler",
                "class_name": "unit_tests.sources.declarative.parsers.testing_components.TestingSomeComponent",
                "subcomponent_field_with_hint": {"field_path": []},
            },
            "subcomponent_field_with_hint",
            DpathExtractor(field_path=[], config={"apikey": "verysecrettoken", "repos": ["airbyte", "airbyte-cloud"]}, parameters={}),
            None,
            id="test_create_custom_component_with_subcomponent_that_must_infer_type_from_explicit_hints",
        ),
        pytest.param(
            {
                "type": "CustomErrorHandler",
                "class_name": "unit_tests.sources.declarative.parsers.testing_components.TestingSomeComponent",
                "basic_field": "expected",
            },
            "basic_field",
            "expected",
            None,
            id="test_create_custom_component_with_built_in_type",
        ),
        pytest.param(
            {
                "type": "CustomErrorHandler",
                "class_name": "unit_tests.sources.declarative.parsers.testing_components.TestingSomeComponent",
                "optional_subcomponent_field": {"type": "RequestOption", "inject_into": "request_parameter", "field_name": "destination"},
            },
            "optional_subcomponent_field",
            RequestOption(inject_into=RequestOptionType.request_parameter, field_name="destination", parameters={}),
            None,
            id="test_create_custom_component_with_subcomponent_wrapped_in_optional",
        ),
        pytest.param(
            {
                "type": "CustomErrorHandler",
                "class_name": "unit_tests.sources.declarative.parsers.testing_components.TestingSomeComponent",
                "list_of_subcomponents": [
                    {"inject_into": "header", "field_name": "store_me"},
                    {"type": "RequestOption", "inject_into": "request_parameter", "field_name": "destination"},
                ],
            },
            "list_of_subcomponents",
            [
                RequestOption(inject_into=RequestOptionType.header, field_name="store_me", parameters={}),
                RequestOption(inject_into=RequestOptionType.request_parameter, field_name="destination", parameters={}),
            ],
            None,
            id="test_create_custom_component_with_subcomponent_wrapped_in_list",
        ),
        pytest.param(
            {
                "type": "CustomErrorHandler",
                "class_name": "unit_tests.sources.declarative.parsers.testing_components.TestingSomeComponent",
                "without_hint": {"inject_into": "request_parameter", "field_name": "missing_hint"},
            },
            "without_hint",
            None,
            None,
            id="test_create_custom_component_with_subcomponent_without_type_hints",
        ),
        pytest.param(
            {
                "type": "CustomErrorHandler",
                "class_name": "unit_tests.sources.declarative.parsers.testing_components.TestingSomeComponent",
                "paginator": {
                    "type": "DefaultPaginator",
                    "pagination_strategy": {"type": "OffsetIncrement", "page_size": 10},
                    "$parameters": {"url_base": "https://physical_100.com"},
                },
            },
            "paginator",
            DefaultPaginator(
                pagination_strategy=OffsetIncrement(
                    page_size=10, config={"apikey": "verysecrettoken", "repos": ["airbyte", "airbyte-cloud"]}, parameters={}
                ),
                url_base="https://physical_100.com",
                config={"apikey": "verysecrettoken", "repos": ["airbyte", "airbyte-cloud"]},
                parameters={},
            ),
            None,
            id="test_create_custom_component_with_subcomponent_that_uses_parameters",
        ),
        pytest.param(
            {
                "type": "CustomErrorHandler",
                "class_name": "unit_tests.sources.declarative.parsers.testing_components.TestingSomeComponent",
                "paginator": {
                    "type": "DefaultPaginator",
                    "pagination_strategy": {"type": "OffsetIncrement", "page_size": 10},
                },
            },
            "paginator",
            None,
            ValueError,
            id="test_create_custom_component_missing_required_field_emits_error",
        ),
    ],
)
def test_create_custom_components(manifest, field_name, expected_value, expected_error):
    if expected_error:
        with pytest.raises(expected_error):
            factory.create_component(CustomErrorHandlerModel, manifest, input_config)
    else:
        custom_component = factory.create_component(CustomErrorHandlerModel, manifest, input_config)
        assert isinstance(custom_component, TestingSomeComponent)

        assert isinstance(getattr(custom_component, field_name), type(expected_value))
        assert getattr(custom_component, field_name) == expected_value


def test_custom_components_do_not_contain_extra_fields():
    custom_substream_partition_router_manifest = {
        "type": "CustomPartitionRouter",
        "class_name": "unit_tests.sources.declarative.parsers.testing_components.TestingCustomSubstreamPartitionRouter",
        "custom_field": "here",
        "extra_field_to_exclude": "should_not_pass_as_parameter",
        "custom_pagination_strategy": {"type": "PageIncrement", "page_size": 100},
        "parent_stream_configs": [
            {
                "type": "ParentStreamConfig",
                "stream": {
                    "type": "DeclarativeStream",
                    "name": "a_parent",
                    "primary_key": "id",
                    "retriever": {
                        "type": "SimpleRetriever",
                        "record_selector": {
                            "type": "RecordSelector",
                            "extractor": {"type": "DpathExtractor", "field_path": []},
                        },
                        "requester": {"type": "HttpRequester", "url_base": "https://airbyte.io", "path": "some"},
                    },
                    "schema_loader": {
                        "type": "JsonFileSchemaLoader",
                        "file_path": "./source_sendgrid/schemas/{{ parameters['name'] }}.yaml",
                    },
                },
                "parent_key": "id",
                "partition_field": "repository_id",
                "request_option": {"type": "RequestOption", "inject_into": "request_parameter", "field_name": "repository_id"},
            }
        ],
    }

    custom_substream_partition_router = factory.create_component(
        CustomPartitionRouterModel, custom_substream_partition_router_manifest, input_config
    )
    assert isinstance(custom_substream_partition_router, TestingCustomSubstreamPartitionRouter)

    assert len(custom_substream_partition_router.parent_stream_configs) == 1
    assert custom_substream_partition_router.parent_stream_configs[0].parent_key.eval({}) == "id"
    assert custom_substream_partition_router.parent_stream_configs[0].partition_field.eval({}) == "repository_id"
    assert custom_substream_partition_router.parent_stream_configs[0].request_option.inject_into == RequestOptionType.request_parameter
    assert custom_substream_partition_router.parent_stream_configs[0].request_option.field_name == "repository_id"

    assert isinstance(custom_substream_partition_router.custom_pagination_strategy, PageIncrement)
    assert custom_substream_partition_router.custom_pagination_strategy.page_size == 100


def test_parse_custom_component_fields_if_subcomponent():
    custom_substream_partition_router_manifest = {
        "type": "CustomPartitionRouter",
        "class_name": "unit_tests.sources.declarative.parsers.testing_components.TestingCustomSubstreamPartitionRouter",
        "custom_field": "here",
        "custom_pagination_strategy": {"type": "PageIncrement", "page_size": 100},
        "parent_stream_configs": [
            {
                "type": "ParentStreamConfig",
                "stream": {
                    "type": "DeclarativeStream",
                    "name": "a_parent",
                    "primary_key": "id",
                    "retriever": {
                        "type": "SimpleRetriever",
                        "record_selector": {
                            "type": "RecordSelector",
                            "extractor": {"type": "DpathExtractor", "field_path": []},
                        },
                        "requester": {"type": "HttpRequester", "url_base": "https://airbyte.io", "path": "some"},
                    },
                    "schema_loader": {
                        "type": "JsonFileSchemaLoader",
                        "file_path": "./source_sendgrid/schemas/{{ parameters['name'] }}.yaml",
                    },
                },
                "parent_key": "id",
                "partition_field": "repository_id",
                "request_option": {"type": "RequestOption", "inject_into": "request_parameter", "field_name": "repository_id"},
            }
        ],
    }

    custom_substream_partition_router = factory.create_component(
        CustomPartitionRouterModel, custom_substream_partition_router_manifest, input_config
    )
    assert isinstance(custom_substream_partition_router, TestingCustomSubstreamPartitionRouter)
    assert custom_substream_partition_router.custom_field == "here"

    assert len(custom_substream_partition_router.parent_stream_configs) == 1
    assert custom_substream_partition_router.parent_stream_configs[0].parent_key.eval({}) == "id"
    assert custom_substream_partition_router.parent_stream_configs[0].partition_field.eval({}) == "repository_id"
    assert custom_substream_partition_router.parent_stream_configs[0].request_option.inject_into == RequestOptionType.request_parameter
    assert custom_substream_partition_router.parent_stream_configs[0].request_option.field_name == "repository_id"

    assert isinstance(custom_substream_partition_router.custom_pagination_strategy, PageIncrement)
    assert custom_substream_partition_router.custom_pagination_strategy.page_size == 100


class TestCreateTransformations:
    # the tabbing matters
    base_parameters = """
                name: "lists"
                primary_key: id
                url_base: "https://api.sendgrid.com"
                schema_loader:
                  name: "{{ parameters.name }}"
                  file_path: "./source_sendgrid/schemas/{{ parameters.name }}.yaml"
                retriever:
                  requester:
                    name: "{{ parameters.name }}"
                    path: "/v3/marketing/lists"
                    request_parameters:
                      page_size: 10
                  record_selector:
                    extractor:
                      field_path: ["result"]
    """

    def test_no_transformations(self):
        content = f"""
        the_stream:
            type: DeclarativeStream
            $parameters:
                {self.base_parameters}
        """
        parsed_manifest = YamlDeclarativeSource._parse(content)
        resolved_manifest = resolver.preprocess_manifest(parsed_manifest)
        resolved_manifest["type"] = "DeclarativeSource"
        stream_manifest = transformer.propagate_types_and_parameters("", resolved_manifest["the_stream"], {})

        stream = factory.create_component(model_type=DeclarativeStreamModel, component_definition=stream_manifest, config=input_config)

        assert isinstance(stream, DeclarativeStream)
        assert [] == stream.retriever.record_selector.transformations

    def test_remove_fields(self):
        content = f"""
        the_stream:
            type: DeclarativeStream
            $parameters:
                {self.base_parameters}
                transformations:
                    - type: RemoveFields
                      field_pointers:
                        - ["path", "to", "field1"]
                        - ["path2"]
        """
        parsed_manifest = YamlDeclarativeSource._parse(content)
        resolved_manifest = resolver.preprocess_manifest(parsed_manifest)
        resolved_manifest["type"] = "DeclarativeSource"
        stream_manifest = transformer.propagate_types_and_parameters("", resolved_manifest["the_stream"], {})

        stream = factory.create_component(model_type=DeclarativeStreamModel, component_definition=stream_manifest, config=input_config)

        assert isinstance(stream, DeclarativeStream)
        expected = [RemoveFields(field_pointers=[["path", "to", "field1"], ["path2"]], parameters={})]
        assert stream.retriever.record_selector.transformations == expected

    def test_add_fields(self):
        content = f"""
        the_stream:
            type: DeclarativeStream
            $parameters:
                {self.base_parameters}
                transformations:
                    - type: AddFields
                      fields:
                        - path: ["field1"]
                          value: "static_value"
        """
        parsed_manifest = YamlDeclarativeSource._parse(content)
        resolved_manifest = resolver.preprocess_manifest(parsed_manifest)
        resolved_manifest["type"] = "DeclarativeSource"
        stream_manifest = transformer.propagate_types_and_parameters("", resolved_manifest["the_stream"], {})

        stream = factory.create_component(model_type=DeclarativeStreamModel, component_definition=stream_manifest, config=input_config)

        assert isinstance(stream, DeclarativeStream)
        expected = [
            AddFields(
                fields=[
                    AddedFieldDefinition(
                        path=["field1"],
                        value=InterpolatedString(string="static_value", default="static_value", parameters={}),
                        parameters={},
                    )
                ],
                parameters={},
            )
        ]
        assert stream.retriever.record_selector.transformations == expected

    def test_default_schema_loader(self):
        component_definition = {
            "type": "DeclarativeStream",
            "name": "test",
            "primary_key": [],
            "retriever": {
                "type": "SimpleRetriever",
                "requester": {
                    "type": "HttpRequester",
                    "url_base": "http://localhost:6767/",
                    "path": "items/",
                    "request_options_provider": {
                        "request_parameters": {},
                        "request_headers": {},
                        "request_body_json": {},
                        "type": "InterpolatedRequestOptionsProvider",
                    },
                    "authenticator": {"type": "BearerAuthenticator", "api_token": "{{ config['api_key'] }}"},
                },
                "record_selector": {"type": "RecordSelector", "extractor": {"type": "DpathExtractor", "field_path": ["items"]}},
                "paginator": {"type": "NoPagination"},
            },
        }
        resolved_manifest = resolver.preprocess_manifest(component_definition)
        ws = ManifestComponentTransformer()
        propagated_source_config = ws.propagate_types_and_parameters("", resolved_manifest, {})
        stream = factory.create_component(
            model_type=DeclarativeStreamModel, component_definition=propagated_source_config, config=input_config
        )
        schema_loader = stream.schema_loader
        assert schema_loader.default_loader._get_json_filepath().split("/")[-1] == f"{stream.name}.json"


@pytest.mark.parametrize(
    "incremental, partition_router, expected_type",
    [
        pytest.param(
            {
                "type": "DatetimeBasedCursor",
                "datetime_format": "%Y-%m-%dT%H:%M:%S.%f%z",
                "start_datetime": "{{ config['start_time'] }}",
                "end_datetime": "{{ config['end_time'] }}",
                "step": "P10D",
                "cursor_field": "created",
                "cursor_granularity": "PT0.000001S",
            },
            None,
            DatetimeBasedCursor,
            id="test_create_simple_retriever_with_incremental",
        ),
        pytest.param(
            None,
            {
                "type": "ListPartitionRouter",
                "values": "{{config['repos']}}",
                "cursor_field": "a_key",
            },
            ListPartitionRouter,
            id="test_create_simple_retriever_with_partition_router",
        ),
        pytest.param(
            {
                "type": "DatetimeBasedCursor",
                "datetime_format": "%Y-%m-%dT%H:%M:%S.%f%z",
                "start_datetime": "{{ config['start_time'] }}",
                "end_datetime": "{{ config['end_time'] }}",
                "step": "P10D",
                "cursor_field": "created",
                "cursor_granularity": "PT0.000001S",
            },
            {
                "type": "ListPartitionRouter",
                "values": "{{config['repos']}}",
                "cursor_field": "a_key",
            },
            PerPartitionCursor,
            id="test_create_simple_retriever_with_incremental_and_partition_router",
        ),
        pytest.param(
            {
                "type": "DatetimeBasedCursor",
                "datetime_format": "%Y-%m-%dT%H:%M:%S.%f%z",
                "start_datetime": "{{ config['start_time'] }}",
                "end_datetime": "{{ config['end_time'] }}",
                "step": "P10D",
                "cursor_field": "created",
                "cursor_granularity": "PT0.000001S",
            },
            [
                {
                    "type": "ListPartitionRouter",
                    "values": "{{config['repos']}}",
                    "cursor_field": "a_key",
                },
                {
                    "type": "ListPartitionRouter",
                    "values": "{{config['repos']}}",
                    "cursor_field": "b_key",
                },
            ],
            PerPartitionCursor,
            id="test_create_simple_retriever_with_partition_routers_multiple_components",
        ),
        pytest.param(None, None, SinglePartitionRouter, id="test_create_simple_retriever_with_no_incremental_or_partition_router"),
    ],
)
def test_merge_incremental_and_partition_router(incremental, partition_router, expected_type):
    stream_model = {
        "type": "DeclarativeStream",
        "retriever": {
            "type": "SimpleRetriever",
            "record_selector": {
                "type": "RecordSelector",
                "extractor": {
                    "type": "DpathExtractor",
                    "field_path": [],
                },
            },
            "requester": {
                "type": "HttpRequester",
                "name": "list",
                "url_base": "orange.com",
                "path": "/v1/api",
            },
        },
    }

    if incremental:
        stream_model["incremental_sync"] = incremental

    if partition_router:
        stream_model["retriever"]["partition_router"] = partition_router

    stream = factory.create_component(model_type=DeclarativeStreamModel, component_definition=stream_model, config=input_config)

    assert isinstance(stream, DeclarativeStream)
    assert isinstance(stream.retriever, SimpleRetriever)
    assert isinstance(stream.retriever.stream_slicer, expected_type)

    if incremental and partition_router:
        assert isinstance(stream.retriever.stream_slicer, PerPartitionCursor)
        if type(partition_router) == list and len(partition_router) > 1:
            assert type(stream.retriever.stream_slicer._partition_router) == CartesianProductStreamSlicer
            assert len(stream.retriever.stream_slicer._partition_router.stream_slicers) == len(partition_router)
    elif partition_router and type(partition_router) == list and len(partition_router) > 1:
        assert isinstance(stream.retriever.stream_slicer, PerPartitionCursor)
        assert len(stream.retriever.stream_slicer.stream_slicerS) == len(partition_router)


def test_simple_retriever_emit_log_messages():
    simple_retriever_model = {
        "type": "SimpleRetriever",
        "record_selector": {
            "type": "RecordSelector",
            "extractor": {
                "type": "DpathExtractor",
                "field_path": [],
            },
        },
        "requester": {"type": "HttpRequester", "name": "list", "url_base": "orange.com", "path": "/v1/api"},
    }

    connector_builder_factory = ModelToComponentFactory(emit_connector_builder_messages=True)
    retriever = connector_builder_factory.create_component(
        model_type=SimpleRetrieverModel,
        component_definition=simple_retriever_model,
        config={},
        name="Test",
        primary_key="id",
        stream_slicer=None,
        transformations=[],
    )

    assert isinstance(retriever, SimpleRetrieverTestReadDecorator)
    assert connector_builder_factory._message_repository._log_level == Level.DEBUG


def test_ignore_retry():
    requester_model = {
        "type": "SimpleRetriever",
        "record_selector": {
            "type": "RecordSelector",
            "extractor": {
                "type": "DpathExtractor",
                "field_path": [],
            },
        },
        "requester": {"type": "HttpRequester", "name": "list", "url_base": "orange.com", "path": "/v1/api"},
    }

    connector_builder_factory = ModelToComponentFactory(disable_retries=True)
    retriever = connector_builder_factory.create_component(
        model_type=SimpleRetrieverModel,
        component_definition=requester_model,
        config={},
        name="Test",
        primary_key="id",
        stream_slicer=None,
        transformations=[]
    )

    assert retriever.max_retries == 0
