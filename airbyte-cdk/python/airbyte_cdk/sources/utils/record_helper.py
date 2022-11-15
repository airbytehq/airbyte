#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import datetime
from typing import Any, Mapping

from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage, AirbyteRecordMessage, AirbyteTraceMessage
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer


def stream_data_to_airbyte_message(
    stream_name: str,
    data_or_message: StreamData,
    transformer: TypeTransformer = TypeTransformer(TransformConfig.NoTransform),
    schema: Mapping[str, Any] = None,
) -> AirbyteMessage:
    if schema is None:
        schema = {}

    if isinstance(data_or_message, dict):
        data = data_or_message
        now_millis = int(datetime.datetime.now().timestamp() * 1000)
        # Transform object fields according to config. Most likely you will
        # need it to normalize values against json schema. By default no action
        # taken unless configured. See
        # docs/connector-development/cdk-python/schemas.md for details.
        transformer.transform(data, schema)  # type: ignore
        message = AirbyteRecordMessage(stream=stream_name, data=data, emitted_at=now_millis)
        return AirbyteMessage(type=MessageType.RECORD, record=message)
    elif isinstance(data_or_message, AirbyteTraceMessage):
        return AirbyteMessage(type=MessageType.TRACE, trace=data_or_message)
    elif isinstance(data_or_message, AirbyteLogMessage):
        return AirbyteMessage(type=MessageType.LOG, log=data_or_message)
    else:
        raise ValueError(f"Unexpected type for data_or_message: {type(data_or_message)}: {data_or_message}")
