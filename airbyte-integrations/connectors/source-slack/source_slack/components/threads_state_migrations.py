# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Any, Mapping

from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration


class ThreadsStateMigration(StateMigration):
    """
    Migrate threads state
    """

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        """
        Check if the stream_state should be migrated
        :param stream_state: The stream_state to potentially migrate
        :return: true if the state is of the expected format and should be migrated. False otherwise.
        """
        return "state" not in stream_state and "float_ts" in stream_state

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Migrate the stream_state. Assumes should_migrate(stream_state) returned True.
        :param stream_state: The stream_state to migrate
        :return: The migrated stream_state
        """
        migrated_stream_state = {"state": {"ts": stream_state["float_ts"]}, "parent_state": {"channel_messages": {"states": []}}}
        return migrated_stream_state
