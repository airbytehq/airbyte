#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import datetime
from typing import Any, Mapping

from airbyte_cdk.models import AirbyteMessage, AirbyteRecordMessage
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources.utils.transform import TypeTransformer


def data_to_airbyte_record(
    stream_name: str, data: Mapping[str, Any], transformer: TypeTransformer, schema: Mapping[str, Any]
) -> AirbyteMessage:
    now_millis = int(datetime.datetime.now().timestamp() * 1000)
    # Transform object fields according to config. Most likely you will
    # need it to normalize values against json schema. By default no action
    # taken unless configured. See
    # docs/connector-development/cdk-python/schemas.md for details.
    transformer.transform(data, schema)  # type: ignore
    message = AirbyteRecordMessage(stream=stream_name, data=data, emitted_at=now_millis)
    return AirbyteMessage(type=MessageType.RECORD, record=message)
