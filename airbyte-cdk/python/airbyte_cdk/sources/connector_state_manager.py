#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, MutableMapping, Union

from airbyte_cdk.models import AirbyteStateMessage, AirbyteStateType


class ConnectorStateManager:
    """
    ConnectorStateManager consolidates the various forms of a stream's incoming state message (STREAM / GLOBAL / LEGACY) under a common
    interface. It also provides methods to extract and update state
    """

    # In the immediate, we only persist legacy which will be used during abstract_source.read(). In the subsequent PRs we will
    # initialize the ConnectorStateManager according to the new per-stream interface received from the platform
    def __init__(self, state: Union[List[AirbyteStateMessage], MutableMapping[str, Any]] = None):
        if isinstance(state, MutableMapping):
            self.legacy = state
        elif self.is_valid_legacy_state(state):
            self.legacy = state[0].data
        else:
            self.legacy = {}

    def get_legacy_state(self) -> MutableMapping[str, Any]:
        return self.legacy

    @staticmethod
    def is_valid_legacy_state(state: List[AirbyteStateMessage]) -> bool:
        return (
            isinstance(state, List)
            and len(state) > 0
            and isinstance(state[0], AirbyteStateMessage)
            and state[0].type == AirbyteStateType.LEGACY
        )
