#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import time
from collections.abc import Mapping as ABCMapping
from typing import Any, Mapping, Optional

from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage, AirbyteRecordMessage, AirbyteTraceMessage
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer


def stream_data_to_airbyte_message(
    stream_name: str,
    data_or_message: StreamData,
    transformer: TypeTransformer = TypeTransformer(TransformConfig.NoTransform),
    schema: Optional[Mapping[str, Any]] = None,
) -> AirbyteMessage:
    if schema is None:
        schema = {}

    match data_or_message:
        case ABCMapping():
            data = dict(data_or_message)
            now_millis = time.time_ns() // 1_000_000
            # Transform object fields according to config. Most likely you will
            # need it to normalize values against json schema. By default no action
            # taken unless configured. See
            # docs/connector-development/cdk-python/schemas.md for details.
            transformer.transform(data, schema)  # type: ignore
            message = AirbyteRecordMessage(stream=stream_name, data=data, emitted_at=now_millis)
            return AirbyteMessage(type=MessageType.RECORD, record=message)
        case AirbyteTraceMessage():
            return AirbyteMessage(type=MessageType.TRACE, trace=data_or_message)
        case AirbyteLogMessage():
            return AirbyteMessage(type=MessageType.LOG, log=data_or_message)
        case _:
            raise ValueError(f"Unexpected type for data_or_message: {type(data_or_message)}: {data_or_message}")
