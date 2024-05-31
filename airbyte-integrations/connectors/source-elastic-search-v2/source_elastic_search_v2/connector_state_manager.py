import logging
from typing import Any, List, Mapping, MutableMapping, Optional, Tuple, Union

from airbyte_cdk.models import (
    AirbyteStateBlob,
    AirbyteStateMessage,
    AirbyteStream,
)
from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager, HashableStreamDescriptor
from airbyte_cdk.sources.streams import Stream
from pydantic import BaseModel
from pydantic import Extra


class ElasticConnectorStateManager(ConnectorStateManager):
    """
    ConnectorStateManager consolidates the various forms of a stream's incoming state message (STREAM / GLOBAL / LEGACY) under a common
    interface. It also provides methods to extract and update state
    """

    class StreamDescriptor(BaseModel):
        class Config:
            extra = Extra.allow

        name: str
        namespace: Optional[str] = None

    class HashableStreamDescriptor(StreamDescriptor):
        """
        Helper class that overrides the existing StreamDescriptor class that is auto generated from the Airbyte Protocol and
        freezes its fields so that it be used as a hash key. This is only marked public because we use it outside for unit tests.
        """

        class Config:
            extra = Extra.allow
            frozen = True

    @classmethod
    def _extract_from_state_message(
        cls,
        state: Optional[Union[List[AirbyteStateMessage], MutableMapping[str, Any]]],
        stream_instance_map: Mapping[str, Union[Stream, AirbyteStream]],
    ) -> Tuple[Optional[AirbyteStateBlob], MutableMapping[HashableStreamDescriptor, Optional[AirbyteStateBlob]]]:
        """
        Takes an incoming list of state messages or the legacy state format and extracts state attributes according to type
        which can then be assigned to the new state manager being instantiated
        :param state: The incoming state input
        :return: A tuple of shared state and per stream state assembled from the incoming state list
        """
        if state is None:
            return None, {}

        streams = cls._create_descriptor_to_stream_state_mapping(state, stream_instance_map)  # type: ignore # We verified state is a dict in _is_legacy_dict_state
        return None, streams

    @staticmethod
    def _create_descriptor_to_stream_state_mapping(
        state: MutableMapping[str, Any], stream_to_instance_map: Mapping[str, Union[Stream, AirbyteStream]]
    ) -> MutableMapping[HashableStreamDescriptor, Optional[AirbyteStateBlob]]:
        """
        Takes incoming state received in the legacy format and transforms it into a mapping of StreamDescriptor to AirbyteStreamState
        :param state: A mapping object representing the complete state of all streams in the legacy format
        :param stream_to_instance_map: A mapping of stream name to stream instance used to retrieve a stream's namespace
        :return: The mapping of all of a sync's streams to the corresponding stream state
        """
        streams = {}
        for stream_name, state_value in state.items():
            namespace = stream_to_instance_map[stream_name].namespace if stream_name in stream_to_instance_map else None
            stream_descriptor = HashableStreamDescriptor(name=stream_name, namespace=namespace)
            streams[stream_descriptor] = AirbyteStateBlob.parse_obj(state_value or {})
        return streams
