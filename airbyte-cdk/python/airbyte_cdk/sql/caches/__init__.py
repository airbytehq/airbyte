# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
"""Base module for all caches."""

from __future__ import annotations

from airbyte_cdk.sql.caches.base import CacheBase

# We export these classes for easy access: `airbyte.caches...`
__all__ = ["CacheBase"]
