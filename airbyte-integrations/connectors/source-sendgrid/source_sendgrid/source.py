#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


class SourceSendgrid(YamlDeclarativeSource):
    def __init__(self) -> None:
        super().__init__(**{"path_to_yaml": "manifest.yaml"})
