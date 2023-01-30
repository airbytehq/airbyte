#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json

import yaml
from airbyte_cdk.models import AirbyteConnectionStatus, ConnectorSpecification
from airbyte_cdk.sources.declarative.checks.connection_checker import ConnectionChecker
from airbyte_cdk.sources.declarative.declarative_source import DeclarativeSource
from airbyte_cdk.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource

"""
This file provides the necessary constructs to interpret a provided declarative YAML configuration file into
source connector.
WARNING: Do not modify this file.
"""


# Declarative Source
class SourceLowcode(DeclarativeSource):
    def __init__(self):
        super().__init__()
        self._source = None

    @property
    def connection_checker(self) -> ConnectionChecker:
        return self._source.connection_check

    def streams(self, config):
        self._init_source(config)
        return self._source.streams(config)

    def spec(self, logger) -> ConnectorSpecification:
        return ConnectorSpecification.parse_raw(
            json.dumps(
                {
                    "documentationUrl": "https://docs.airbyte.com/integrations/sources/posthog",
                    "connectionSpecification": {
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "title": "PostHog Spec",
                        "type": "object",
                        "required": ["manifest"],
                        "properties": {
                            "manifest": {
                                "type": "string",
                                "airbyte_secret": True,
                                "title": "API Key",
                                "description": 'API Key. See the <a href="https://docs.airbyte.com/integrations/sources/posthog">docs</a> for information on how to generate this key.',
                                "airbyte_hidden": True,
                            },
                        },
                    },
                }
            )
        )

    def check(self, logger, config) -> AirbyteConnectionStatus:
        self._init_source(config)
        return self._source.check(logger, config)

    def read(self, logger, config, catalog, state):
        self._init_source(config)
        return self._source.read(logger, config, catalog, state)

    def _init_source(self, config):
        if self._source is None:
            self._source = ManifestDeclarativeSource(yaml.safe_load(config["manifest"]), True)
