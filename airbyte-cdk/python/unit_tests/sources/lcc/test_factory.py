#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from airbyte_cdk.sources.lcc.parsers.factory import LowCodeComponentFactory
from airbyte_cdk.sources.lcc.parsers.yaml_parser import YamlParser
from airbyte_cdk.sources.lcc.requesters.request_params.interpolated_request_parameter_provider import InterpolatedRequestParameterProvider

factory = LowCodeComponentFactory()

parser = YamlParser()

input_config = dict()


def test():
    content = """
    limit: 50
    offset_request_parameters:
      offset: "{{ next_page_token['offset'] }}"
      limit: "*ref(limit)"
    offset_pagination_request_parameters:
      class_name: airbyte_cdk.sources.lcc.requesters.request_params.interpolated_request_parameter_provider.InterpolatedRequestParameterProvider
      request_parameters: "*ref(offset_request_parameters)"
    """
    config = parser.parse(content)
    offset_pagination_request_parameters = factory.create_component(config["offset_pagination_request_parameters"], input_config)
    assert type(offset_pagination_request_parameters) == InterpolatedRequestParameterProvider
    assert offset_pagination_request_parameters._config == input_config
