#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

"""Source Marketo entry point.

All streams are now fully declarative (defined in ``manifest.yaml``).
Bulk export streams (Leads + Activities) use the CDK ``AsyncRetriever``
pattern with custom components defined in ``components.py``.
"""

import logging
from typing import Any, Mapping

from airbyte_cdk.models import AirbyteConnectionStatus
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


class SourceMarketo(YamlDeclarativeSource):
    """Source Marketo — declarative connector for the Marketo REST API."""

    def __init__(self) -> None:
        super().__init__(path_to_yaml="manifest.yaml")

    def check(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        # TODO(CDK): Remove this workaround once the CDK fixes the issue where
        # ``hasattr(source, "dynamic_streams")`` in CheckStream.check_connection
        # triggers eager resolution of HttpComponentsResolver with an empty
        # config, causing Jinja UndefinedError. This accesses the private
        # ``_config`` attribute on ManifestDeclarativeSource.
        self._config = config
        return super().check(logger, config)
