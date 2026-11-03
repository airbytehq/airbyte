from datetime import datetime, timezone

import freezegun
from components import CustomerBalanceTransactionsEventsParentStateMigration


@freezegun.freeze_time("2026-11-03T16:00:00Z")
def test_cold_state_migration_seeds_events_parent_at_now() -> None:
    migration = CustomerBalanceTransactionsEventsParentStateMigration(config={})

    assert migration.should_migrate({})
    assert migration.migrate({}) == {"parent_state": {"cbt_customer_events": {"updated": int(datetime.now(timezone.utc).timestamp())}}}


@freezegun.freeze_time("2026-11-03T16:00:00Z")
def test_placeholder_state_migration_uses_default_start_and_preserves_other_state() -> None:
    start_epoch = int(datetime(2017, 1, 25, tzinfo=timezone.utc).timestamp())
    stream_state = {
        "state": {"created": start_epoch},
        "parent_state": {"customers": {"updated": start_epoch}},
        "other": "preserved",
    }
    migration = CustomerBalanceTransactionsEventsParentStateMigration(config={})

    assert migration.should_migrate(stream_state)
    assert migration.migrate(stream_state) == {
        "state": {"created": start_epoch},
        "parent_state": {
            "customers": {"updated": start_epoch},
            "cbt_customer_events": {"updated": int(datetime.now(timezone.utc).timestamp())},
        },
        "other": "preserved",
    }
    assert stream_state["parent_state"] == {"customers": {"updated": start_epoch}}


def test_migration_skips_state_with_events_parent_cursor() -> None:
    migration = CustomerBalanceTransactionsEventsParentStateMigration(config={})
    stream_state = {"parent_state": {"cbt_customer_events": {"updated": 123}}}

    assert not migration.should_migrate(stream_state)
