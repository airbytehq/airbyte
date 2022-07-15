#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


class SourceExchangeRatesTutorial(YamlDeclarativeSource):
    def __init__(self):
        super().__init__(**{"path_to_yaml": "./source_exchange_rates_tutorial/connector_definition.yaml"})
