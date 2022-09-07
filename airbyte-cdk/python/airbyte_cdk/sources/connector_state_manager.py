#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import copy
from typing import Any, List, Mapping, MutableMapping, Union

from airbyte_cdk.models import AirbyteStateBlob, AirbyteStateMessage, AirbyteStateType


class ConnectorStateManager:
    """
    ConnectorStateManager consolidates the various forms of a stream's incoming state message (STREAM / GLOBAL / LEGACY) under a common
    interface. It also provides methods to extract and update state
    """

    # In the immediate, we only persist legacy which will be used during abstract_source.read(). In the subsequent PRs we will
    # initialize the ConnectorStateManager according to the new per-stream interface received from the platform
    def __init__(self, state: Union[List[AirbyteStateMessage], MutableMapping[str, Any]] = None):
        if not state:
            self.legacy = {}
        elif self.is_migrated_legacy_state(state):
            # The legacy state format received from the platform is parsed and stored as a single AirbyteStateMessage when reading
            # the file. This is used for input backwards compatibility.
            self.legacy = state[0].data
        elif isinstance(state, MutableMapping):
            # In the event that legacy state comes in as its original JSON object format, no changes to the input need to be made
            self.legacy = state
        else:
            raise ValueError("Input state should come in the form of list of Airbyte state messages or a mapping of states")

    def get_stream_state(self, namespace: str, stream_name: str) -> AirbyteStateBlob:
        # todo implement in upcoming PRs
        pass

    def get_legacy_state(self) -> MutableMapping[str, Any]:
        """
        Returns a deep copy of the current legacy state dictionary made up of the state of all streams for a connector
        :return: A copy of the legacy state
        """
        return copy.deepcopy(self.legacy, {})

    def update_state_for_stream(self, namespace: str, stream_name: str, value: Mapping[str, Any]):
        # todo implement in upcoming PRs
        pass

    @staticmethod
    def is_migrated_legacy_state(state: List[AirbyteStateMessage]) -> bool:
        return (
            isinstance(state, List)
            and len(state) == 1
            and isinstance(state[0], AirbyteStateMessage)
            and state[0].type == AirbyteStateType.LEGACY
        )
