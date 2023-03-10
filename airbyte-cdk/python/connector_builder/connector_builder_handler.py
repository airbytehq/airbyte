#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import datetime
from typing import List

from airbyte_cdk.models import AirbyteRecordMessage
from airbyte_cdk.sources.declarative.declarative_source import DeclarativeSource
from airbyte_cdk.utils.traced_exception import AirbyteTracedException

from dataclasses import asdict, dataclass
from copy import deepcopy
import json
from json import JSONDecodeError
from typing import Any, Dict, Iterable, Iterator, Mapping, Optional, Union
from urllib.parse import parse_qs, urlparse

from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage, Type
from airbyte_cdk.utils.schema_inferrer import SchemaInferrer
import logging
from airbyte_protocol.models.airbyte_protocol import ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, SyncMode, DestinationSyncMode



def list_streams() -> AirbyteRecordMessage:
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

