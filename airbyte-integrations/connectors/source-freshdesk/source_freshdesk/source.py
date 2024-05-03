#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


class SourceFreshdesk(YamlDeclarativeSource):
    def __init__(self):
        print()  # just adding this to trigger connectors-ci for this connector to validate changes don't impact low-code
        super().__init__(**{"path_to_yaml": "manifest.yaml"})
