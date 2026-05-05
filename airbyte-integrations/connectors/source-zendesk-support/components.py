# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from dataclasses import InitVar, dataclass
from typing import Any, List, Mapping

import requests

from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration


class ForceFailError(RuntimeError):
    """Plain Python exception raised by `ForceFailExtractor` for pre-release testing.

    DO NOT MERGE — inherits from `RuntimeError` rather than
    `airbyte_cdk.utils.traced_exception.AirbyteTracedException` so the CDK has
    to wrap a vanilla Python exception (no curated `failure_type`, no
    user-facing `message`). This mirrors what the platform sees when a
    connector hits an unhandled bug in the wild.
    """


@dataclass
class ForceFailExtractor(RecordExtractor):
    """Record extractor that force-fails every record extraction.

    DO NOT MERGE — this extractor exists solely to produce a pre-release image
    that fails every sync on the read path. The HTTP request, authentication,
    and response are all left intact; the failure is raised when the platform
    asks the connector to extract records from the response. Every stream's
    `read` therefore fails with a `ForceFailError` (a plain `RuntimeError`
    subclass).
    """

    parameters: InitVar[Mapping[str, Any]]

    def extract_records(self, response: requests.Response) -> List[Mapping[str, Any]]:
        raise ForceFailError("source-zendesk-support pre-release force-fail injection. DO NOT MERGE.")


class ZendeskSupportExtractorEvents(RecordExtractor):
    def extract_records(self, response: requests.Response) -> List[Mapping[str, Any]]:
        try:
            records = response.json().get("ticket_events") or []
        except requests.exceptions.JSONDecodeError:
            records = []

        events = []
        for record in records:
            for event in record.get("child_events", []):
                if event.get("event_type") == "Comment":
                    for prop in ["via_reference_id", "ticket_id", "timestamp"]:
                        event[prop] = record.get(prop)

                    # https://github.com/airbytehq/oncall/issues/1001
                    if not isinstance(event.get("via"), dict):
                        event["via"] = None
                    events.append(event)
        return events


class ZendeskSupportAttributeDefinitionsExtractor(RecordExtractor):
    def extract_records(self, response: requests.Response) -> List[Mapping[str, Any]]:
        try:
            records = []
            for definition in response.json()["definitions"]["conditions_all"]:
                definition["condition"] = "all"
                records.append(definition)
            for definition in response.json()["definitions"]["conditions_any"]:
                definition["condition"] = "any"
                records.append(definition)
        except requests.exceptions.JSONDecodeError:
            records = []
        return records


class TicketsStateMigration(StateMigration):
    """Migrates tickets stream state from generated_timestamp cursor to updated_at cursor.

    The tickets stream was switched from the Incremental Export API (which uses generated_timestamp)
    to the Export Search Results API (which filters by updated_at). Existing connections may have
    state with generated_timestamp as the cursor field, which needs to be migrated to updated_at.
    """

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        return "generated_timestamp" in stream_state

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        return {"updated_at": stream_state["generated_timestamp"]}
