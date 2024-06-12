# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from abc import abstractmethod
from typing import Any, Mapping


class StateMigration:
    @abstractmethod
    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        """
        Check if the stream_state should be migrated

        :param stream_state: The stream_state to potentially migrate
        :return: true if the state is of the expected format and should be migrated. False otherwise.
        """

    @abstractmethod
    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Migrate the stream_state. Assumes should_migrate(stream_state) returned True.

        :param stream_state: The stream_state to migrate
        :return: The migrated stream_state
        """
