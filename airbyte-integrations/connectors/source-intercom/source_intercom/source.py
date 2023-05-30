#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource

"""
This file provides the necessary constructs to interpret a provided declarative YAML configuration file into
source connector.

WARNING: Do not modify this file.
"""


# Declarative Source
class SourceIntercom(YamlDeclarativeSource):
    def __init__(self):
        super().__init__(**{"path_to_yaml": "manifest.yaml"})


    def _configure_logger_level(self, logger: logging.Logger):
        """
        Set the log level to logging.DEBUG if debug mode
        """
        logger.setLevel(logging.DEBUG)
