#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from __future__ import annotations

from airbyte_cdk.sources.types import Config, ConnectionDefinition, FieldPointer, Record, StreamSlice, StreamState

# Note: This package originally contained class definitions for low-code CDK types, but we promoted them into the Python CDK.
# We've migrated connectors in the repository to reference the new location, but these assignments are used to retain backwards
# compatibility for sources created by OSS customers or on forks. This can be removed when we start bumping major versions.

FieldPointer = FieldPointer
Config = Config
ConnectionDefinition = ConnectionDefinition
StreamState = StreamState
Record = Record
StreamSlice = StreamSlice
