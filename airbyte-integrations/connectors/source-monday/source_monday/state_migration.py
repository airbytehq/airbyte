
#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping

from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration


class MondayStateMigration(StateMigration):
    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        del stream_state["activity_logs"]
        return stream_state

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        return "activity_logs" in stream_state
