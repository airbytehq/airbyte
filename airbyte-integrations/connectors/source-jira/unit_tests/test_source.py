#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import responses
from conftest import _YAML_FILE_PATH

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


@responses.activate
def test_streams(config):
    source = YamlDeclarativeSource(config=config, catalog=None, state=None, path_to_yaml=str(_YAML_FILE_PATH))
    streams = source.streams(config)
    expected_streams_number = 55
    assert len(streams) == expected_streams_number
