# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping

from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration


_DEFAULT_START_DATE = "2017-01-25T00:00:00Z"
_EVENT_RETENTION_SECONDS = 30 * 24 * 60 * 60


@dataclass
class CustomerBalanceTransactionsEventsParentStateMigration(StateMigration):
    config: Mapping[str, Any]

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        parent_state = stream_state.get("parent_state")
        return not isinstance(parent_state, Mapping) or "cbt_customer_events" not in parent_state

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        state_parent = stream_state.get("parent_state")
        parent_state = dict(state_parent) if isinstance(state_parent, Mapping) else {}
        customer_state = parent_state.get("customers")
        customers_updated = (
            int(customer_state["updated"]) if isinstance(customer_state, Mapping) and customer_state.get("updated") is not None else None
        )
        start_date = self.config.get("start_date") or _DEFAULT_START_DATE
        if isinstance(start_date, datetime):
            start_datetime = start_date
        else:
            start_datetime = datetime.fromisoformat(str(start_date).replace("Z", "+00:00"))
        if start_datetime.tzinfo is None:
            start_datetime = start_datetime.replace(tzinfo=timezone.utc)

        start_epoch = int(start_datetime.timestamp())
        now = int(datetime.now(timezone.utc).timestamp())
        events_updated = (
            now if customers_updated is None or customers_updated <= start_epoch else max(customers_updated, now - _EVENT_RETENTION_SECONDS)
        )

        return {
            **stream_state,
            "parent_state": {
                **parent_state,
                "cbt_customer_events": {"updated": events_updated},
            },
        }
