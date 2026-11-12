#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import copy
from datetime import datetime, timezone
from typing import Any, Mapping, Optional

from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration
from airbyte_cdk.sources.types import Config
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from airbyte_cdk.utils.datetime_helpers import ab_datetime_format, ab_datetime_try_parse


class TwilioDateTimeTypeTransformer(TypeTransformer):
    """
    Twilio API returns datetime in two formats:
    - RFC2822, like "Fri, 11 Dec 2020 04:28:40 +0000";
    - ISO8601, like "2020-12-11T04:29:09Z".
    We only transform RFC2822 values (detected by the presence of ", ").

    Note:
    This could be implemented using a transformation, but to avoid cluttering the manifest with many transformations,
    this normalization is implemented here.
    """

    def __init__(self, *args, **kwargs):
        # apply this transformer during schema normalization phase(s)
        config = TransformConfig.DefaultSchemaNormalization | TransformConfig.CustomSchemaNormalization
        super().__init__(config)
        # register our custom transform
        self.registerCustomTransform(self.get_transform_function())

    @staticmethod
    def get_transform_function():
        def custom_transform_function(original_value: Any, field_schema: Mapping[str, Any]) -> Any:
            if original_value and field_schema.get("format") == "date-time":
                try:
                    dt = datetime.strptime(original_value, "%a, %d %b %Y %H:%M:%S %z").astimezone(timezone.utc)
                    return ab_datetime_format(dt, "%Y-%m-%dT%H:%M:%SZ")
                except ValueError:
                    pass
            return original_value

        return custom_transform_function


class TwilioStateMigration(StateMigration):
    """
    Ensure legacy partitions include an empty `parent_slice` required by the SubstreamPartitionRouter.

    Initial:
      {
        "states": [
          {
            "partition": { "subresource_uri": "/2010-04-01/Accounts/AC123/Addresses.json" },
            "cursor": { "date_created": "2022-01-01T00:00:00Z" }
          }
        ]
      }

    Final:
      {
        "states": [
          {
            "partition": {
              "subresource_uri": "/2010-04-01/Accounts/AC123/Addresses.json",
              "parent_slice": {}
            },
            "cursor": { "date_created": "2022-01-01T00:00:00Z" }
          }
        ]
      }
    """

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        for state in stream_state.get("states", []):
            state["partition"]["parent_slice"] = {}
        return stream_state

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        if stream_state and any("parent_slice" not in state["partition"] for state in stream_state.get("states", [])):
            return True
        return False


class TwilioStalePartitionStateMigration(StateMigration):
    """
    Drop per-partition cursors that are older than the global cursor so those partitions resume from the global cursor.

    The global cursor (`state`) only advances when a sync completes, after every partition has been read up to that sync's end.
    A per-partition cursor only advances when its partition returns a record, so an account with no recent records keeps an old
    cursor. Because a per-partition cursor takes precedence over the global cursor, the next sync re-reads (and re-emits) that
    partition's history from the old cursor. The CDK starts partitions without a per-partition cursor from the global cursor
    minus `lookback_window` (the duration of the last sync), which covers records written while that sync was running.

    Initial:
      {
        "use_global_cursor": false,
        "states": [
          {"partition": {"subresource_uri": ".../AC1/Messages.json", "parent_slice": {}}, "cursor": {"date_sent": "2026-05-20 10:00:00Z"}},
          {"partition": {"subresource_uri": ".../AC2/Messages.json", "parent_slice": {}}, "cursor": {"date_sent": "2025-01-01 00:00:00Z"}}
        ],
        "state": {"date_sent": "2026-05-21 08:00:00Z"},
        "lookback_window": 3600
      }

    Final:
      {
        "use_global_cursor": false,
        "states": [],
        "state": {"date_sent": "2026-05-21 08:00:00Z"},
        "lookback_window": 3600
      }

    Per-partition cursors at or ahead of the global cursor (eg. checkpoints of an interrupted sync) are kept unchanged.
    """

    cursor_field: str
    config: Config
    parameters: Mapping[str, Any]

    def __init__(self, cursor_field: str, config: Config, parameters: Mapping[str, Any]):
        self._cursor_field = InterpolatedString.create(cursor_field, parameters=parameters or {}).eval(config)

    @staticmethod
    def _parse(value: Any) -> Optional[datetime]:
        if not isinstance(value, str):
            return None
        return ab_datetime_try_parse(value.replace(" ", "T", 1))

    def _global_cursor(self, stream_state: Mapping[str, Any]) -> Optional[datetime]:
        global_state = stream_state.get("state")
        if not isinstance(global_state, Mapping) or self._cursor_field not in global_state:
            return None
        return self._parse(global_state[self._cursor_field])

    def _is_stale(self, partition_state: Mapping[str, Any], global_cursor: datetime) -> bool:
        cursor = partition_state.get("cursor")
        if not isinstance(cursor, Mapping):
            return False
        partition_cursor = self._parse(cursor.get(self._cursor_field))
        return partition_cursor is not None and partition_cursor < global_cursor

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        global_cursor = self._global_cursor(stream_state)
        migrated_state = dict(stream_state)
        migrated_state["states"] = [state for state in stream_state["states"] if not self._is_stale(state, global_cursor)]
        return migrated_state

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        if not stream_state or stream_state.get("use_global_cursor") or not isinstance(stream_state.get("states"), list):
            return False
        global_cursor = self._global_cursor(stream_state)
        if global_cursor is None:
            return False
        return any(self._is_stale(state, global_cursor) for state in stream_state["states"])


class TwilioAlertsStateMigration(StateMigration):
    """
    Migrates legacy `alerts` state to low-code shape. Previously, the stream incorrectly used per partition state.

    Initial:
    {
        "states" : [
          {
            "partition" : {},
            "cursor" : {
              "date_generated" : "2025-08-05T16:43:50Z"
            }
          }
        ]
    }

    Final:
    {
        "date_generated" : "2025-08-05T16:43:50Z"
    }
    """

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        return stream_state["states"][0]["cursor"]

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        if (
            stream_state
            and "states" in stream_state
            and stream_state["states"]
            and "cursor" in stream_state["states"][0]
            and "date_generated" in stream_state["states"][0]["cursor"]
        ):
            return True
        return False


class TwilioUsageRecordsStateMigration(StateMigration):
    """
    Migrate legacy `usage_records` state to low-code shape.

    - Add empty `parent_slice` to each partition.
    - Drop legacy `partition.date_created`.
    - Run if any partition lacks `parent_slice`.

    Initial:
    {
      "states": [
        {
          "cursor": { "start_date": "2025-08-21T00:00:00Z" },
          "partition": {
            "account_sid": "ACdade166c12e160e9ed0a6088226718fb",
            "date_created": "Tue, 17 Nov 2020 04:08:53 +0000"
          }
        },
        {
          "cursor": { "start_date": "2025-08-21T00:00:00Z" },
          "partition": {
            "account_sid": "AC4cac489c46197c9ebc91c840120a4dee",
            "date_created": "Wed, 25 Nov 2020 09:36:42 +0000"
          }
        }
      ]
    }

    Final:
    {
      "states": [
        {
          "cursor": { "start_date": "2025-08-21T00:00:00Z" },
          "partition": { "account_sid": "ACdade166c12e160e9ed0a6088226718fb", "parent_slice": {} }
        },
        {
          "cursor": { "start_date": "2025-08-21T00:00:00Z" },
          "partition": { "account_sid": "AC4cac489c46197c9ebc91c840120a4dee", "parent_slice": {} }
        }
      ]
    }
    """

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        new_state = {"states": []}
        for state in stream_state.get("states", []):
            partition_state = {}
            if "partition" not in state or "account_sid" not in state["partition"]:
                continue

            partition_state["partition"] = {"account_sid": state["partition"]["account_sid"], "parent_slice": {}}
            partition_state["cursor"] = state.get("cursor", {})

            new_state["states"].append(partition_state)
        return new_state

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        if stream_state and any("parent_slice" not in state["partition"] for state in stream_state.get("states", [])):
            return True
        return False


class TwilioMessageMediaStateMigration(StateMigration):
    """
    Reshape Message Media state to include hierarchical parent slices back to the
    Messages collection. Low-code derives `message_media` partitions from `messages`,
    so the state must retain the media-level `subresource_uri` and also include
    `parent_slice.subresource_uri` pointing to the Messages collection
    (e.g., “…/Messages.json”). States missing `partition.subresource_uri` are skipped.

    Initial:
      {
        "states": [
          {
            "partition": { "subresource_uri": "/2010-04-01/Accounts/AC123/Messages/SM123/Media.json" },
            "cursor": { "date_created": "2022-11-01T00:00:00Z" }
          }
        ]
      }

    Final:
      {
        "states": [
          {
            "partition": {
              "subresource_uri": "/2010-04-01/Accounts/AC123/Messages/SM123/Media.json",
              "parent_slice": {
                "subresource_uri": "/2010-04-01/Accounts/AC123/Messages.json",
                "parent_slice": {}
              }
            },
            "cursor": { "date_created": "2022-11-01T00:00:00Z" }
          }
        ]
      }
    """

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        new_state = {"states": []}
        for state in stream_state.get("states", []):
            partition_state = {}
            if not "partition" in state or "subresource_uri" not in state["partition"]:
                continue

            partition_state["partition"] = {
                "subresource_uri": state["partition"]["subresource_uri"],
                "parent_slice": {
                    "subresource_uri": state["partition"]["subresource_uri"].split("Messages")[0] + "Messages.json",
                    "parent_slice": {},
                },
            }
            partition_state["cursor"] = state.get("cursor", {})
            new_state["states"].append(partition_state)

        return new_state

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        if stream_state and any("parent_slice" not in state["partition"] for state in stream_state.get("states", [])):
            return True
        return False


_CONFERENCE_STATUSES = ("init", "in-progress", "completed")


class TwilioConferencesStateMigration(StateMigration):
    """
    Duplicate each conferences partition for every conference status value
    (`init`, `in-progress`, `completed`) after adding the `ListPartitionRouter`
    for the Status filter.

    Initial:
      {
        "states": [
          {
            "partition": {
              "subresource_uri": "/2010-04-01/Accounts/AC123/Conferences.json",
              "parent_slice": {}
            },
            "cursor": { "date_created": "2022-11-01T00:00:00Z" }
          }
        ]
      }

    Final:
      {
        "states": [
          {
            "partition": {
              "conference_status": "init",
              "subresource_uri": "/2010-04-01/Accounts/AC123/Conferences.json",
              "parent_slice": {}
            },
            "cursor": { "date_created": "2022-11-01T00:00:00Z" }
          },
          {
            "partition": {
              "conference_status": "in-progress",
              "subresource_uri": "/2010-04-01/Accounts/AC123/Conferences.json",
              "parent_slice": {}
            },
            "cursor": { "date_created": "2022-11-01T00:00:00Z" }
          },
          {
            "partition": {
              "conference_status": "completed",
              "subresource_uri": "/2010-04-01/Accounts/AC123/Conferences.json",
              "parent_slice": {}
            },
            "cursor": { "date_created": "2022-11-01T00:00:00Z" }
          }
        ]
      }
    """

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        new_states: list[dict[str, Any]] = []
        for state in stream_state.get("states", []):
            for status in _CONFERENCE_STATUSES:
                new_partition = copy.deepcopy(state["partition"])
                new_partition["conference_status"] = status
                new_states.append({"partition": new_partition, "cursor": copy.deepcopy(state.get("cursor", {}))})
        return {"states": new_states}

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        if stream_state and any("conference_status" not in state.get("partition", {}) for state in stream_state.get("states", [])):
            return True
        return False
