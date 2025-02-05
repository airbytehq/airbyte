#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping

from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration
from airbyte_cdk.sources.types import Config


ARCHIVED_SMS = {"archived": "true", "campaign_type": "sms"}
NOT_ARCHIVED_SMS = {"archived": "false", "campaign_type": "sms"}
ARCHIVED_EMAIL = {"archived": "true", "campaign_type": "email"}
NOT_ARCHIVED_EMAIL = {"archived": "false", "campaign_type": "email"}


class CampaignsStateMigration(StateMigration):
    """
    Moves old state for per partition format. Cursor value from archived object to partition with archived=true.

    Example input state:
    {
        "updated_at": "2020-10-10T00:00:00+00:00",
        "archived": {
          "updated_at": "2021-10-10T00:00:00+00:00"
        }
      }
    Example output state:
    {
        "partition":{ "archived":"true","campaign_type":"sms" },
        "cursor":{ "updated_at":"2021-10-10T00:00:00+00:00" }
    }
    {
        "partition":{ "archived":"false","campaign_type":"sms" },
        "cursor":{ "updated_at":"2020-10-10T00:00:00+00:00" }
    }
    """

    declarative_stream: DeclarativeStream
    config: Config

    def __init__(self, declarative_stream: DeclarativeStream, config: Config):
        self._config = config
        self.declarative_stream = declarative_stream
        self._cursor = declarative_stream.incremental_sync
        self._parameters = declarative_stream.parameters
        self._cursor_field = InterpolatedString.create(self._cursor.cursor_field, parameters=self._parameters).eval(self._config)

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        return "states" not in stream_state

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        if not self.should_migrate(stream_state):
            return stream_state

        is_archived_updated_at = stream_state["archived"][self._cursor.cursor_field]
        is_not_archived_updated_at = stream_state[self._cursor.cursor_field]

        migrated_stream_state = {
            "states": [
                {"partition": ARCHIVED_SMS, "cursor": {self._cursor.cursor_field: is_archived_updated_at}},
                {"partition": NOT_ARCHIVED_SMS, "cursor": {self._cursor.cursor_field: is_not_archived_updated_at}},
                {"partition": ARCHIVED_EMAIL, "cursor": {self._cursor.cursor_field: is_archived_updated_at}},
                {"partition": NOT_ARCHIVED_EMAIL, "cursor": {self._cursor.cursor_field: is_not_archived_updated_at}},
            ]
        }

        return migrated_stream_state
