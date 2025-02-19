#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
from abc import ABC
from typing import Any, Mapping

from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration
from airbyte_cdk.sources.types import Config


ARCHIVED_EMAIL = {"archived": "true", "campaign_type": "email"}
NOT_ARCHIVED_EMAIL = {"archived": "false", "campaign_type": "email"}

ARCHIVED = {"archived": "true"}
NOT_ARCHIVED = {"archived": "false"}

DEFAULT_START_DATE = "2012-01-01T00:00:00Z"


class ArchivedToPerPartitionStateMigration(StateMigration, ABC):
    """
    Updates old format state to new per partitioned format.
    Partitions: [{archived: True}, {archived: False}]
    Default built in airbyte cdk migration will recognise only top-level field cursor value(updated_at),
    but for partition {archived: True} source should use cursor value from archived object.

    Example input state:
    {
        "updated_at": "2020-10-10T00:00:00+00:00",
        "archived": {
          "updated_at": "2021-10-10T00:00:00+00:00"
        }
    }

    Example output state:
    {
        "partition":{ "archived":"true" },
        "cursor":{ "updated_at":"2021-10-10T00:00:00+00:00" }
    }
    {
        "partition":{ "archived":"false" },
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

    def get_archived_cursor_value(self, stream_state: Mapping[str, Any]):
        return stream_state.get("archived", {}).get(self._cursor.cursor_field, self._config.get("start_date", DEFAULT_START_DATE))

    def get_not_archived_cursor_value(self, stream_state: Mapping[str, Any]):
        return stream_state.get(self._cursor.cursor_field, self._config.get("start_date", DEFAULT_START_DATE))

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        return bool("states" not in stream_state and stream_state)

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        if not self.should_migrate(stream_state):
            return stream_state
        is_archived_updated_at = self.get_archived_cursor_value(stream_state)
        is_not_archived_updated_at = self.get_not_archived_cursor_value(stream_state)

        migrated_stream_state = {
            "states": [
                {"partition": ARCHIVED, "cursor": {self._cursor.cursor_field: is_archived_updated_at}},
                {"partition": NOT_ARCHIVED, "cursor": {self._cursor.cursor_field: is_not_archived_updated_at}},
            ]
        }
        return migrated_stream_state


class CampaignsStateMigration(ArchivedToPerPartitionStateMigration):
    """
    Campaigns stream has 2 partition field: archived and campaign_type(email, sms).
    Previous API version didn't return sms in campaigns output so we need to migrate only email partition.

    Example input state:
    {
        "updated_at": "2020-10-10T00:00:00+00:00",
        "archived": {
          "updated_at": "2021-10-10T00:00:00+00:00"
        }
      }
    Example output state:
    {
        "partition":{ "archived":"true","campaign_type":"email" },
        "cursor":{ "updated_at":"2021-10-10T00:00:00+00:00" }
    }
    {
        "partition":{ "archived":"false","campaign_type":"email" },
        "cursor":{ "updated_at":"2020-10-10T00:00:00+00:00" }
    }
    """

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        if not self.should_migrate(stream_state):
            return stream_state
        is_archived_updated_at = self.get_archived_cursor_value(stream_state)
        is_not_archived_updated_at = self.get_not_archived_cursor_value(stream_state)

        migrated_stream_state = {
            "states": [
                {"partition": ARCHIVED_EMAIL, "cursor": {self._cursor.cursor_field: is_archived_updated_at}},
                {"partition": NOT_ARCHIVED_EMAIL, "cursor": {self._cursor.cursor_field: is_not_archived_updated_at}},
            ]
        }
        return migrated_stream_state
