import time
from typing import Any, Optional
from airbyte_cdk.models import AirbyteMessage, Type, AirbyteTraceMessage, TraceType, AirbyteAnalyticsTraceMessage


def create_analytics_message(type: str, value: Optional[Any]):
    return AirbyteMessage(type=Type.TRACE, trace=AirbyteTraceMessage(type=TraceType.ANALYTICS, emitted_at=time.time() * 1000, analytics=AirbyteAnalyticsTraceMessage(type=type, value=str(value) if value is not None else None)))
