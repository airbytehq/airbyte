# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
"""Sources connectors module for Airbyte."""

from __future__ import annotations

from airbyte_cdk.sql.sources import base, util
from airbyte_cdk.sql.sources.base import Source
from airbyte_cdk.sql.sources.registry import (
    ConnectorMetadata,
    get_available_connectors,
    get_connector_metadata,
)
from airbyte_cdk.sql.sources.util import (
    get_benchmark_source,
    get_source,
)


__all__ = [
    # Submodules
    "base",
    "util",
    # Factories
    "get_source",
    "get_benchmark_source",
    # Helper Functions
    "get_available_connectors",
    "get_connector_metadata",
    # Classes
    "Source",
    "ConnectorMetadata",
]
