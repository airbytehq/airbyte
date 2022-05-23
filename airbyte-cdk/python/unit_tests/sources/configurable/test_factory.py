#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.sources.configurable.configurable_stream import ConfigurableStream
from airbyte_cdk.sources.configurable.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.configurable.parsers.factory import LowCodeComponentFactory
from airbyte_cdk.sources.configurable.parsers.yaml_parser import YamlParser
from airbyte_cdk.sources.configurable.requesters.request_params.interpolated_request_parameter_provider import (
    InterpolatedRequestParameterProvider,
)
from airbyte_cdk.sources.configurable.requesters.requester import HttpMethod
from airbyte_cdk.sources.configurable.retrievers.simple_retriever import SimpleRetriever
from airbyte_cdk.sources.configurable.schema.json_schema import JsonSchema

factory = LowCodeComponentFactory()

parser = YamlParser()

input_config = {"apikey": "verysecrettoken"}


def test_factory():
    content = """
    limit: 50
    offset_request_parameters:
      offset: "{{ next_page_token['offset'] }}"
      limit: "*ref(limit)"
    offset_pagination_request_parameters:
      class_name: airbyte_cdk.sources.configurable.requesters.request_params.interpolated_request_parameter_provider.InterpolatedRequestParameterProvider
      request_parameters: "*ref(offset_request_parameters)"
    """
    config = parser.parse(content)
    offset_pagination_request_parameters = factory.create_component(config["offset_pagination_request_parameters"], input_config)()
    assert type(offset_pagination_request_parameters) == InterpolatedRequestParameterProvider
    assert offset_pagination_request_parameters._config == input_config
    assert offset_pagination_request_parameters._interpolation._mapping["offset"] == "{{ next_page_token['offset'] }}"


def test_interpolate_config():
    content = """
authenticator:
  class_name: airbyte_cdk.sources.streams.http.requests_native_auth.token.TokenAuthenticator
  token: "{{ config['apikey'] }}"
    """
    config = parser.parse(content)
    authenticator = factory.create_component(config["authenticator"], input_config)()
    assert authenticator._tokens == ["verysecrettoken"]


def test_full_config():
    # FIXME: some objects need to be checked
    # FIXME: the ones with class: instead of class_name!
    content = """
decoder:
  class_name: "airbyte_cdk.sources.configurable.decoders.json_decoder.JsonDecoder"
extractor:
  class_name: airbyte_cdk.sources.configurable.extractors.jq.JqExtractor
  decoder: "*ref(decoder)"
metadata_paginator:
  class_name: "airbyte_cdk.sources.configurable.requesters.paginators.next_page_url_paginator.NextPageUrlPaginator"
  next_page_token_template:
    "next_page_url": "{{ decoded_response['_metadata']['next'] }}"
next_page_url_from_token_partial:
  class_name: "airbyte_cdk.sources.configurable.interpolation.interpolated_string.InterpolatedString"
  string: "{{ next_page_token['next_page_url'] }}"
request_parameters_provider:
  class_name: airbyte_cdk.sources.configurable.requesters.request_params.interpolated_request_parameter_provider.InterpolatedRequestParameterProvider
requester:
  class_name: airbyte_cdk.sources.configurable.requesters.http_requester.HttpRequester
  name: "{{ kwargs['name'] }}"
  url_base: "https://api.sendgrid.com/v3/"
  http_method: "GET"
  authenticator:
    class_name: airbyte_cdk.sources.streams.http.requests_native_auth.token.TokenAuthenticator
    token: "{{ config['apikey'] }}"
  request_parameters_provider: "*ref(request_parameters_provider)"
  retrier:
    class_name: airbyte_cdk.sources.configurable.requesters.retriers.default_retrier.DefaultRetrier
retriever:
  class_name: "airbyte_cdk.sources.configurable.retrievers.simple_retriever.SimpleRetriever"
  name: "{{ kwargs['name'] }}"
  state:
    class_name: airbyte_cdk.sources.configurable.states.dict_state.DictState
  stream_slicer:
    class_name: airbyte_cdk.sources.configurable.stream_slicers.single_slice.SingleSlice
  paginator:
    class_name: airbyte_cdk.sources.configurable.requesters.paginators.no_pagination.NoPagination
  primary_key: "{{ kwargs['primary_key'] }}"
partial_stream:
  class_name: "airbyte_cdk.sources.configurable.configurable_stream.ConfigurableStream"
  schema_loader:
    class_name: airbyte_cdk.sources.configurable.schema.json_schema.JsonSchema
    file_path: "./source_sendgrid/schemas/{{kwargs['name']}}.json"
  cursor_field: [ ]
list_stream:
  partial: "*ref(partial_stream)"
  kwargs:
    name: "lists"
    primary_key: "id"
  retriever:
    partial: "*ref(retriever)"
    requester:
      partial: "*ref(requester)"
      path:
        partial: "*ref(next_page_url_from_token_partial)"
        default: "marketing/lists"
    paginator:
      partial: "*ref(metadata_paginator)"
    extractor:
      partial: "*ref(extractor)"
      transform: ".result[]"
    """
    config = parser.parse(content)

    stream_config = config["list_stream"]
    assert stream_config["class_name"] == "airbyte_cdk.sources.configurable.configurable_stream.ConfigurableStream"
    assert stream_config["cursor_field"] == []
    stream = factory.create_component(stream_config, input_config)()
    assert type(stream) == ConfigurableStream
    assert stream.primary_key == "id"
    assert stream.name == "lists"
    assert type(stream._schema_loader) == JsonSchema
    assert type(stream._retriever) == SimpleRetriever
    assert stream._retriever._requester._method == HttpMethod.GET
    assert stream._retriever._requester._authenticator._tokens == ["verysecrettoken"]
    assert type(stream._retriever._extractor._decoder) == JsonDecoder
    assert stream._retriever._extractor._transform == ".result[]"
