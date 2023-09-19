#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


# Declarative Source
class SourceAudienceProject(YamlDeclarativeSource):
    def __init__(self):
        super().__init__(**{"path_to_yaml": "manifest.yaml"})
