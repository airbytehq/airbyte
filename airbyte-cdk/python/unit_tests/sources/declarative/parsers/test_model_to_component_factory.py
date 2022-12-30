#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.sources.declarative.checks import CheckStream
from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream
from airbyte_cdk.sources.declarative.decoders import JsonDecoder
from airbyte_cdk.sources.declarative.extractors import DpathExtractor, RecordFilter, RecordSelector
from airbyte_cdk.sources.declarative.models import CheckStream as CheckStreamModel
from airbyte_cdk.sources.declarative.models import DeclarativeStream as DeclarativeStreamModel
from airbyte_cdk.sources.declarative.models import Spec as SpecModel
from airbyte_cdk.sources.declarative.parsers.manifest_component_transformer import ManifestComponentTransformer
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.declarative.requesters import HttpRequester
from airbyte_cdk.sources.declarative.requesters.requester import HttpMethod
from airbyte_cdk.sources.declarative.retrievers import SimpleRetriever
from airbyte_cdk.sources.declarative.schema import JsonFileSchemaLoader
from airbyte_cdk.sources.declarative.spec import Spec
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource

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
requester:
  type: HttpRequester
  name: "{{ options['name'] }}"
  url_base: "https://api.sendgrid.com/v3/"
  http_method: "GET"
  authenticator:
    type: BearerAuthenticator
    api_token: "{{ config['apikey'] }}"
  request_parameters_provider: "*ref(request_options_provider)"
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

    # todo more thoroughly cover every part of the components being tested
    assert isinstance(stream, DeclarativeStream)
    assert stream.primary_key == "id"
    assert stream.name == "lists"

    assert isinstance(stream.schema_loader, JsonFileSchemaLoader)
    assert stream.schema_loader._get_json_filepath() == "./source_sendgrid/schemas/lists.json"

    assert isinstance(stream.retriever, SimpleRetriever)
    assert stream.retriever.primary_key == "{{ options['primary_key'] }}"
    assert stream.retriever.name == "lists"

    assert isinstance(stream.retriever.record_selector, RecordSelector)

    assert isinstance(stream.retriever.record_selector.extractor, DpathExtractor)
    assert isinstance(stream.retriever.record_selector.extractor.decoder, JsonDecoder)
    assert [fp.eval(input_config) for fp in stream.retriever.record_selector.extractor.field_pointer] == ["lists"]

    assert isinstance(stream.retriever.record_selector.record_filter, RecordFilter)
    assert stream.retriever.record_selector.record_filter._filter_interpolator.condition == "{{ record['id'] > stream_state['id'] }}"

    assert isinstance(stream.retriever.requester, HttpRequester)
    assert stream.retriever.requester.http_method == HttpMethod.GET
    assert stream.retriever.requester.authenticator._token.eval(input_config) == "verysecrettoken"

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


def test_construct_schemas():
    # tbd if we need this
    pass
