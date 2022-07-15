#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


class SourceSendgrid(YamlDeclarativeSource):
    """
    This is a sample low-code connector.
    It still uses the existing spec.yaml file
    """

    def __init__(self):
        super().__init__(**{"path_to_yaml": "./source_sendgrid/sendgrid_bounces2.yaml"})
