#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Optional


class StreamAvailability:
    @classmethod
    def available(cls) -> "StreamAvailability":
        return cls(True)

    @classmethod
    def unavailable(cls, reason: str) -> "StreamAvailability":
        return cls(False, reason)

    def __init__(self, available: bool, reason: Optional[str] = None) -> None:
        self._available = available
        self._reason = reason

        if not available:
            assert reason, "A reason needs to be provided if the stream is not available"

    @property
    def is_available(self) -> bool:
        """
        :return: True if the stream is available. False if the stream is not
        """
        return self._available

    @property
    def reason(self) -> Optional[str]:
        """
        :return: A message describing why the stream is not available. If the stream is available, this should return None.
        """
        return self._reason
