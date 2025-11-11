#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from typing import Mapping

from pydantic.v1 import BaseModel

from airbyte_cdk.sources.declarative.checks.check_dynamic_stream import CheckDynamicStream
from airbyte_cdk.sources.declarative.checks.check_stream import (
    CheckStream,
    DynamicStreamCheckConfig,
)
from airbyte_cdk.sources.declarative.checks.connection_checker import ConnectionChecker
from airbyte_cdk.sources.declarative.models import (
    CheckDynamicStream as CheckDynamicStreamModel,
)
from airbyte_cdk.sources.declarative.models import (
    CheckStream as CheckStreamModel,
)

COMPONENTS_CHECKER_TYPE_MAPPING: Mapping[str, type[BaseModel]] = {
    "CheckStream": CheckStreamModel,
    "CheckDynamicStream": CheckDynamicStreamModel,
}

__all__ = ["CheckStream", "CheckDynamicStream", "ConnectionChecker", "DynamicStreamCheckConfig"]
