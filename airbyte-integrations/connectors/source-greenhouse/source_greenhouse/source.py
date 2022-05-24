#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.sources.configurable.yaml_configurable_source import YamlConfigurableSource


class SourceGreenhouse(YamlConfigurableSource):
    """
    This is a sample low-code connector.
    It still uses the existing spec.yaml file
    """

    def __init__(self):
        super().__init__(**{"path_to_yaml": "./source_greenhouse/greenhouse.yaml"})
