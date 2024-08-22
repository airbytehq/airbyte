#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from dataclasses import InitVar, dataclass, field
from typing import Annotated, Any, Mapping

import serpyco_rs
from airbyte_protocol_dataclasses.models import *
from orjson import orjson
from serpyco_rs.metadata import Alias


@dataclass
class AirbyteStateBlob:
    kwargs: InitVar[Mapping[str, Any]]

    # def __post_init__(self, kwargs):
    #     self.__dict__.update(kwargs)
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


class AirbyteStateBlobType(serpyco_rs.CustomType[AirbyteStateBlob, str]):
    def serialize(self, value: AirbyteStateBlob) -> Dict[str, Any]:
        return orjson.loads(orjson.dumps(value))

    def deserialize(self, value: Dict[str, Any]) -> AirbyteStateBlob:
        return AirbyteStateBlob(value)

    def get_json_schema(self):
        return {"type": "object"}


def custom_type_resolver(t: type) -> serpyco_rs.CustomType | None:
    if t is AirbyteStateBlob:
        return AirbyteStateBlobType()
    return None


# TODO: ref and move Serializers

AirbyteStreamStateSerializer = serpyco_rs.Serializer(AirbyteStreamState, omit_none=True, custom_type_resolver=custom_type_resolver)
AirbyteStateMessageSerializer = serpyco_rs.Serializer(AirbyteStateMessage, omit_none=True, custom_type_resolver=custom_type_resolver)

AirbyteMessageSerializer = serpyco_rs.Serializer(AirbyteMessage, omit_none=True, custom_type_resolver=custom_type_resolver)

AirbyteCatalogSerializer = serpyco_rs.Serializer(AirbyteCatalog, omit_none=True)

ConfiguredAirbyteCatalogSerializer = serpyco_rs.Serializer(ConfiguredAirbyteCatalog, omit_none=True)
ConfiguredAirbyteStreamSerializer = serpyco_rs.Serializer(ConfiguredAirbyteStream, omit_none=True)

AdvancedAuthSerializer = serpyco_rs.Serializer(AdvancedAuth, omit_none=True)
ConnectorSpecificationSerializer = serpyco_rs.Serializer(ConnectorSpecification, omit_none=True)
