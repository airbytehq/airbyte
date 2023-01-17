#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
import yaml

"""
This file provides the necessary constructs to interpret a provided declarative YAML configuration file into
source connector.

WARNING: Do not modify this file.
"""


# Declarative Source
class SourceLowcode(YamlDeclarativeSource):
    def __init__(self):
        data = {}
        # with open('/airbyte/integration_code/source_lowcode/manifest.yaml') as infile:
        #     data = json.load(infile)
        # with open('/airbyte/integration_code/source_lowcode/real_manifest.yaml', 'w') as outfile:
        #     yaml.dump(data, outfile, default_flow_style=False)
        super().__init__(**{"path_to_yaml": "/manifest.yaml", "debug": False })
