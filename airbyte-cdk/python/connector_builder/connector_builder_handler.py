#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import datetime

from airbyte_cdk.models import AirbyteMessage, AirbyteRecordMessage, Type
from airbyte_cdk.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


def list_streams() -> AirbyteMessage:
    raise NotImplementedError


def stream_read() -> AirbyteMessage:
    raise NotImplementedError


def resolve_manifest(source: ManifestDeclarativeSource) -> AirbyteMessage:
    try:
        return AirbyteMessage(
            type=Type.RECORD,
            record=AirbyteRecordMessage(
                data={"manifest": source.resolved_manifest},
                emitted_at=_emitted_at(),
                stream="resolve_manifest",
            ),
        )
    except Exception as exc:
        error = AirbyteTracedException.from_exception(exc, message="Error resolving manifest.")
        return error.as_airbyte_message()


def _emitted_at():
    return int(datetime.now().timestamp()) * 1000
