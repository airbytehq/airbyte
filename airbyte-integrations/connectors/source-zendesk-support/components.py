# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import copy
import os
from typing import Any, Callable, List, Mapping, MutableMapping

import requests

from airbyte_cdk.models import ConnectorSpecification
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration
from airbyte_cdk.sources.declarative.spec.spec import Spec
from airbyte_cdk.sources.declarative.transformations.config_transformations.config_transformation import (
    ConfigTransformation,
)


# Values of `credentials.credentials` whose oneOf branch a new Airbyte Cloud source must not offer.
CLOUD_HIDDEN_AUTH_OPTIONS = frozenset({"api_token", "oauth2.0"})

CLOUD_CREDENTIALS_DESCRIPTION = (
    "Authenticate with `OAuth2.0 with Refresh Token`. Sources that already use an API token or legacy OAuth keep "
    "working, but Zendesk deactivates all API tokens on April 30, 2027, so re-authenticate them with OAuth before then."
)


def is_cloud_edition() -> bool:
    """
    The platform sets `AIRBYTE_EDITION` on every connector operation, and the registry generates the Cloud spec with
    `AIRBYTE_EDITION=CLOUD`. `DEPLOYMENT_MODE` (what the CDK's `is_cloud_environment()` reads) is not set for check
    and discover in Cloud, so it is not used here.
    """
    return os.environ.get("AIRBYTE_EDITION", "").casefold() == "cloud"


def hide_auth_options_for_cloud(spec: ConnectorSpecification) -> ConnectorSpecification:
    """
    Mark the `API Token` and `OAuth2.0 (Legacy)` branches of `credentials` as `airbyte_hidden`, so the Cloud setup
    form only offers `OAuth2.0 with Refresh Token`. `airbyte_hidden` is a form hint only: the branches stay in the
    schema, so a stored config that uses one of them still validates and keeps passing check, discover and read.
    """
    connection_specification = copy.deepcopy(dict(spec.connectionSpecification))
    credentials = connection_specification["properties"]["credentials"]
    for option in credentials["oneOf"]:
        if option["properties"]["credentials"]["const"] in CLOUD_HIDDEN_AUTH_OPTIONS:
            option["airbyte_hidden"] = True
    credentials["description"] = CLOUD_CREDENTIALS_DESCRIPTION
    spec.connectionSpecification = connection_specification
    return spec


def _edition_aware(generate_spec: Callable[[Spec], ConnectorSpecification]) -> Callable[[Spec], ConnectorSpecification]:
    def generate_spec_for_edition(self: Spec) -> ConnectorSpecification:
        spec = generate_spec(self)
        return hide_auth_options_for_cloud(spec) if is_cloud_edition() else spec

    generate_spec_for_edition._zendesk_support_edition_aware = True  # type: ignore[attr-defined]
    return generate_spec_for_edition


# A manifest cannot vary its spec by edition, so the CDK's spec generation is wrapped here. The wrapper only takes
# effect once this module is imported, which during `spec` happens only because the manifest's spec block references
# `CloudSpecHook` below. The guard keeps a second import of this module from wrapping the wrapper.
if not getattr(Spec.generate_spec, "_zendesk_support_edition_aware", False):
    Spec.generate_spec = _edition_aware(Spec.generate_spec)  # type: ignore[method-assign]


class CloudSpecHook(ConfigTransformation):
    """
    Changes no config. It is listed under `spec.config_normalization_rules.transformations` because the CDK imports
    this module only when it builds a custom component, and `spec` builds nothing but the spec block. Removing it
    from the manifest makes the Cloud spec show every authentication option again.
    """

    def transform(self, config: MutableMapping[str, Any]) -> None:
        return None


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
    """Migrates tickets stream state from the `updated_at` cursor back to `generated_timestamp`.

    Background: v5.2.0 switched the `tickets` stream from the Incremental Ticket Export API
    (keyed on `generated_timestamp`) to the Export Search Results API (filtered/checkpointed on
    `updated_at`). Because Zendesk only bumps `updated_at` when an update generates a ticket
    event, automation/macro/system-driven updates were silently dropped. We revert the stream to
    `generated_timestamp`, so existing connections carrying `updated_at`-based state must be
    migrated back.

    Backfill: to recover every ticket missed while the regression was live, the migrated cursor
    is clamped back to an absolute floor of 2026-03-01T00:00:00Z (epoch 1772323200) — just before
    v5.2.0 merged (2026-03-12) / rolled out to Cloud (~2026-03-24). This guarantees a complete
    one-time backfill regardless of when a connection upgrades (a relative "N-day" window computed
    at migration time would drift forward and miss the earliest affected tickets). `min(...)`
    ensures we only ever pull the cursor back, never forward, so connections whose cursor has not
    yet reached the floor are left untouched.

    Only connections that ran the buggy `updated_at`-cursor versions carry `updated_at` state, so
    keying `should_migrate` on that field means the floor is applied exactly once (on the first
    sync after upgrade); subsequent syncs write `generated_timestamp` state and are left alone.
    Connections still on a pre-5.2.0 `generated_timestamp` cursor were never broken and are not
    migrated.
    """

    # 2026-03-01T00:00:00Z
    BACKFILL_FLOOR = 1772323200

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        return bool(stream_state) and "updated_at" in stream_state

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        try:
            cursor_value = int(stream_state["updated_at"])
        except (KeyError, TypeError, ValueError):
            cursor_value = self.BACKFILL_FLOOR
        return {"generated_timestamp": min(cursor_value, self.BACKFILL_FLOOR)}
