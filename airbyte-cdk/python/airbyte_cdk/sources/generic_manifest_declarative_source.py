#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.models import AirbyteConnectionStatus, ConnectorSpecification

from .declarative.checks.connection_checker import ConnectionChecker
from .declarative.declarative_source import DeclarativeSource
from .declarative.manifest_declarative_source import ManifestDeclarativeSource


class GenericManifestDeclarativeSource(DeclarativeSource):
    def __init__(self):
        self._source = None

    @property
    def connection_checker(self) -> ConnectionChecker:
        return self._source.connection_check

    def streams(self, config):
        self._init_source(config)
        return self._source.streams(config)

    def spec(self, logger) -> ConnectorSpecification:
        if self._source is not None:
            # return spec if source got configured already by another call
            return self._source.spec(logger)
        raise Exception("this connector does not support the spec command as the spec is passed in as part of the config to other commands")

    def check(self, logger, config) -> AirbyteConnectionStatus:
        self._init_source(config)
        return self._source.check(logger, config)

    def read(self, logger, config, catalog, state):
        self._init_source(config)
        return self._source.read(logger, config, catalog, state)

    def _init_source(self, config):
        if self._source is None:
            self._source = ManifestDeclarativeSource(config["__injected_declarative_manifest"], True)

    def configure(self, config, temp_dir):
        config = super().configure(config, temp_dir)
        self._init_source(config)
        return config
