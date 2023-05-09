#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json

import pytest
from source_freshsales.source import SourceFreshsales


@pytest.fixture(scope="session", name="config")
def config_fixture():
    with open("secrets/config.json", "r") as config_file:
        return json.load(config_file)


@pytest.fixture(name="stream_args")
def stream_args(config):
    return SourceFreshsales().get_input_stream_args(config['api_key'], config["domain_name"])
