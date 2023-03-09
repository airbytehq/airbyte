#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import datetime
from typing import Union

from airbyte_cdk.models import AirbyteMessage, AirbyteRecordMessage
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


def list_streams() -> AirbyteRecordMessage:
    raise NotImplementedError


def stream_read() -> AirbyteRecordMessage:
    raise NotImplementedError


def resolve_manifest(source) -> Union[AirbyteMessage, AirbyteRecordMessage]:
    try:
        return AirbyteRecordMessage(
            data={"manifest": source.resolved_manifest},
            emitted_at=_emitted_at(),
            stream="",
        )
    except Exception as exc:
        error = AirbyteTracedException.from_exception(exc, message="Error resolving manifest.")
        return error.as_airbyte_message()


def _emitted_at():
    return int(datetime.now().timestamp()) * 1000
