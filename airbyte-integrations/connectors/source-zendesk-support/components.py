# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import Any, List, Mapping

import requests

from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration


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
    """Migrates tickets stream state from the updated_at cursor back to generated_timestamp.

    The tickets stream was reverted from the Export Search Results API (which filtered by
    updated_at) to the Incremental Ticket Export API (which is keyed on generated_timestamp),
    because updated_at is not a reliable cursor: Zendesk only bumps updated_at when an update
    generates a ticket event, so automation/macro/system-driven changes were silently dropped.

    Connections that ran the updated_at-based version stored state under updated_at (epoch
    seconds). This migration carries that watermark over to generated_timestamp. Because
    generated_timestamp is always >= updated_at for a given ticket, resuming from the prior
    updated_at watermark is safe and does not skip records.
    """

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        return "updated_at" in stream_state and "generated_timestamp" not in stream_state

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        return {"generated_timestamp": stream_state["updated_at"]}
