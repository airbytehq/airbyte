#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import traceback
from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional

from airbyte_protocol_dataclasses.models import SyncMode

from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage, Level
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.checkpoint import Cursor
from airbyte_cdk.sources.utils.record_helper import stream_data_to_airbyte_message
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


class IdentitiesStream(Stream, ABC):
    """
    The identities stream. A full refresh stream to sync identities from a certain domain.
    The load_identity_groups method manage the logic to get such data.
    """

    IDENTITIES_STREAM_NAME = "identities"

    is_resumable = False

    def __init__(self) -> None:
        super().__init__()
        self._cursor: MutableMapping[str, Any] = {}

    @property
    def state(self) -> MutableMapping[str, Any]:
        return self._cursor

    @state.setter
    def state(self, value: MutableMapping[str, Any]) -> None:
        """State setter, accept state serialized by state getter."""
        self._cursor = value

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any] | AirbyteMessage]:
        try:
            identity_groups = self.load_identity_groups()
            for record in identity_groups:
                yield stream_data_to_airbyte_message(self.name, record)
        except AirbyteTracedException as exc:
            # Re-raise the exception to stop the whole sync immediately as this is a fatal error
            raise exc
        except Exception as e:
            yield AirbyteMessage(
                type=MessageType.LOG,
                log=AirbyteLogMessage(
                    level=Level.ERROR,
                    message=f"Error trying to read identities: {e} stream={self.name}",
                    stack_trace=traceback.format_exc(),
                ),
            )

    @abstractmethod
    def load_identity_groups(self) -> Iterable[Dict[str, Any]]:
        raise NotImplementedError("Implement this method to read identity records")

    @property
    def name(self) -> str:
        return self.IDENTITIES_STREAM_NAME

    def get_cursor(self) -> Optional[Cursor]:
        return None
