# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import time
from typing import Any, Optional

from airbyte_cdk.models import (
    AirbyteAnalyticsTraceMessage,
    AirbyteMessage,
    AirbyteTraceMessage,
    TraceType,
    Type,
)


def create_analytics_message(type: str, value: Optional[Any]) -> AirbyteMessage:
    return AirbyteMessage(
        type=Type.TRACE,
        trace=AirbyteTraceMessage(
            type=TraceType.ANALYTICS,
            emitted_at=time.time() * 1000,
            analytics=AirbyteAnalyticsTraceMessage(
                type=type, value=str(value) if value is not None else None
            ),
        ),
    )
