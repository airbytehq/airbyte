#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from dataclasses import InitVar
from typing import Annotated, Mapping

from airbyte_protocol_dataclasses.models import *
from serpyco_rs.metadata import Alias


@dataclass
class AirbyteStateBlob:
    kwargs: InitVar[Mapping[str, Any]]

    def __init__(self, *args, **kwargs):
        # Set any attribute passed in through kwargs
        for arg in args:
            self.__dict__.update(arg)
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __eq__(self, other: AirbyteStateBlob):
        return bool(self.__dict__ == other.__dict__)


@dataclass
class AirbyteStreamState:
    stream_descriptor: StreamDescriptor
    stream_state: Optional[AirbyteStateBlob] = None


@dataclass
class AirbyteGlobalState:
    stream_states: List[AirbyteStreamState]
    shared_state: Optional[AirbyteStateBlob] = None


@dataclass
class AirbyteStateMessage:
    type: Optional[AirbyteStateType] = None
    stream: Optional[AirbyteStreamState] = None
    global_: Annotated[AirbyteGlobalState | None, Alias("global")] = None
    data: Optional[Dict[str, Any]] = None
    sourceStats: Optional[AirbyteStateStats] = None
    destinationStats: Optional[AirbyteStateStats] = None


@dataclass
class AirbyteMessage:
    type: Type
    log: Optional[AirbyteLogMessage] = None
    spec: Optional[ConnectorSpecification] = None
    connectionStatus: Optional[AirbyteConnectionStatus] = None
    catalog: Optional[AirbyteCatalog] = None
    record: Optional[AirbyteRecordMessage] = None
    state: Optional[AirbyteStateMessage] = None
    trace: Optional[AirbyteTraceMessage] = None
    control: Optional[AirbyteControlMessage] = None
