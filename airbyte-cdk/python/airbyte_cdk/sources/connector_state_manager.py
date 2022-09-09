#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import copy
from typing import Any, List, Mapping, MutableMapping, Optional, Tuple, Union

from airbyte_cdk.models import AirbyteStateBlob, AirbyteStateMessage, AirbyteStateType, StreamDescriptor
from airbyte_cdk.sources.streams import Stream
from pydantic import Extra


class HashableStreamDescriptor(StreamDescriptor):
    """
    Helper class that overrides the existing StreamDescriptor class that is auto generated from the Airbyte Protocol and
    freezes its fields so that it be used as a hash key. This is only marked public because we use it outside for unit tests.
    """

    class Config:
        extra = Extra.allow
        frozen = True


class ConnectorStateManager:
    """
    ConnectorStateManager consolidates the various forms of a stream's incoming state message (STREAM / GLOBAL / LEGACY) under a common
    interface. It also provides methods to extract and update state
    """

    def __init__(self, stream_instance_map: Mapping[str, Stream], state: Union[List[AirbyteStateMessage], MutableMapping[str, Any]] = None):
        shared_state, per_stream_states = self._extract_from_state_message(state, stream_instance_map)
        self.shared_state = shared_state
        self.per_stream_states = per_stream_states

    def get_stream_state(self, stream_name: str, namespace: Optional[str]) -> Mapping[str, Any]:
        """
        Retrieves the state of a given stream based on its descriptor (name + namespace) including any global shared state.
        Stream state takes precedence over shared state when there are conflicts
        :param stream_name: Name of the stream being fetched
        :param namespace: Namespace of the stream being fetched
        :return: The combined shared state and per-stream state of a stream
        """
        combined_state = {}
        if self.shared_state:
            combined_state.update(self.shared_state.dict())
        target_state = self.per_stream_states.get(HashableStreamDescriptor(name=stream_name, namespace=namespace))
        if target_state:
            combined_state.update(target_state.dict())
        return combined_state

    def get_legacy_state(self) -> MutableMapping[str, Any]:
        """
        Using the current per-stream state, creates a mapping of all the stream states for the connector being synced
        :return: A deep copy of the mapping of stream name to stream state value
        """
        return {descriptor.name: per_stream.dict() for descriptor, per_stream in self.per_stream_states.items() if per_stream is not None}

    def update_state_for_stream(self, stream_name: str, namespace: str, value: Mapping[str, Any]):
        stream_descriptor = HashableStreamDescriptor(name=stream_name, namespace=namespace)
        self.per_stream_states[stream_descriptor] = AirbyteStateBlob.parse_obj(value)

    @classmethod
    def _extract_from_state_message(
        cls, state: Union[List[AirbyteStateMessage], MutableMapping[str, Any]], stream_instance_map: Mapping[str, Stream]
    ) -> Tuple[Optional[AirbyteStateBlob], MutableMapping[HashableStreamDescriptor, AirbyteStateBlob]]:
        """
        Takes an incoming list of state messages or the legacy state format and extracts state attributes according to type
        which can then be assigned to the new state manager being instantiated
        :param state: The incoming state input
        :return: A tuple of shared state, per stream state, and legacy state assembled from the incoming state list
        """
        if state is None:
            return None, {}

        # Incoming pure legacy object format
        if isinstance(state, dict):
            streams = cls._create_stream_from_state_object(state, stream_instance_map)
            return None, streams

        if not isinstance(state, List):
            raise ValueError("Input state should come in the form of list of Airbyte state messages or a mapping of states")

        if cls._is_migrated_legacy_state(state):
            streams = cls._create_stream_from_state_object(state[0].data, stream_instance_map)
            return None, streams

        if cls._is_global_state(state):
            global_state = state[0].global_
            shared_state = copy.deepcopy(global_state.shared_state, {})
            streams = {
                HashableStreamDescriptor(
                    name=per_state.stream_descriptor.name, namespace=per_state.stream_descriptor.namespace
                ): per_state.stream_state
                for per_state in global_state.stream_states
            }
            return shared_state, streams

        # Assuming all prior conditions were not met this is a per-stream list of states
        streams = {
            HashableStreamDescriptor(
                name=per_state.stream.stream_descriptor.name, namespace=per_state.stream.stream_descriptor.namespace
            ): per_state.stream.stream_state
            for per_state in state
            if per_state.type == AirbyteStateType.STREAM and hasattr(per_state, "stream")
        }
        return None, streams

    @staticmethod
    def _create_stream_from_state_object(
        state: MutableMapping[str, Any], stream_to_instance_map: Mapping[str, Stream]
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
            streams[stream_descriptor] = AirbyteStateBlob.parse_obj(state_value)
        return streams

    @staticmethod
    def _is_migrated_legacy_state(state: List[AirbyteStateMessage]) -> bool:
        return len(state) == 1 and isinstance(state[0], AirbyteStateMessage) and state[0].type == AirbyteStateType.LEGACY

    @staticmethod
    def _is_global_state(state: List[AirbyteStateMessage]) -> bool:
        return len(state) == 1 and isinstance(state[0], AirbyteStateMessage) and state[0].type == AirbyteStateType.GLOBAL
