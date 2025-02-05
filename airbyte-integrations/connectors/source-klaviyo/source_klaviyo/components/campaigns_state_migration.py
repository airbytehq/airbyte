#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping

from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration
from airbyte_cdk.sources.types import Config


class CampaignsStateMigration(StateMigration):
    """

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
        print("should_migrate")
        return "partition" not in stream_state

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        if not self.should_migrate(stream_state):
            return stream_state

        print("migration logic")
