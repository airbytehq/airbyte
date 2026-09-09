#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

"""Unit tests for `ReportsStateMigration` and `ReportsCreateTimeStateMigration`.

End-to-end coverage of the migration lives in `test_incremental_reports.py`, which proves it is
wired into the stream. These tests cover the state shapes that are awkward to reach through a
read: per-partition cursors, idempotence, and unparseable values.
"""

import pytest


_LEGACY_DAY = "20251107"
_LEGACY_DAY_AS_CURSOR = "2025-11-07T00:00:00.000000Z"
# A `createTime` as the API returns it, and the same value in the cursor's own format.
_API_TIMESTAMP = "2026-09-03T00:00:00Z"
_API_TIMESTAMP_AS_CURSOR = "2026-09-03T00:00:00.000000Z"


class _MigrationChain:
    """Applies the manifest's `state_migrations` the way the CDK does: in order, each gated on its own `should_migrate`."""

    def __init__(self, components_module):
        self.migrations = [components_module.ReportsStateMigration(), components_module.ReportsCreateTimeStateMigration()]
        self._to_cursor_value = self.migrations[1]._to_cursor_value

    def should_migrate(self, stream_state):
        return any(migration.should_migrate(stream_state) for migration in self.migrations)

    def migrate(self, stream_state):
        for migration in self.migrations:
            if migration.should_migrate(stream_state):
                stream_state = dict(migration.migrate(stream_state))
        return stream_state


@pytest.fixture
def migration(components_module):
    return _MigrationChain(components_module)


def test_pre_low_code_migration_only_rebuilds_the_shape(components_module):
    """The first migration is the original one: it knows nothing about `createTime`."""
    migration = components_module.ReportsStateMigration()

    assert migration.should_migrate({"date": 20251107}) is True
    assert migration.should_migrate({"state": {"date": _LEGACY_DAY}}) is False
    assert migration.migrate({"date": 20251107}) == {
        "state": {"date": _LEGACY_DAY},
        "parent_state": {"report": {"state": {"date": _LEGACY_DAY}}},
    }


def test_create_time_migration_ignores_pre_low_code_state(components_module):
    assert components_module.ReportsCreateTimeStateMigration().should_migrate({"date": 20251107}) is False


def test_pre_low_code_state_is_rebuilt_and_seeds_the_parent(migration):
    """Pre-1.1.0 state was a bare day at the top level, with no parent state at all."""
    migrated = migration.migrate({"date": 20251107})

    # The child keeps its own `date` cursor: it is a real column in the downloaded CSV.
    assert migrated["state"] == {"date": _LEGACY_DAY}
    assert migrated["parent_state"]["report"]["state"] == {"createTime": _LEGACY_DAY_AS_CURSOR}


@pytest.mark.parametrize(
    "legacy_value, expected",
    [
        pytest.param(_LEGACY_DAY, _LEGACY_DAY_AS_CURSOR, id="day_copied_off_the_child_by_1.1.0-1.3.4"),
        pytest.param(_API_TIMESTAMP, _API_TIMESTAMP_AS_CURSOR, id="create_time_under_the_old_key_from_1.3.5"),
        pytest.param(_API_TIMESTAMP_AS_CURSOR, _API_TIMESTAMP_AS_CURSOR, id="already_in_the_cursor_format"),
    ],
)
def test_parent_cursor_is_rekeyed_and_normalised(migration, legacy_value, expected):
    stream_state = {
        "state": {"date": _LEGACY_DAY},
        "parent_state": {"report": {"state": {"date": legacy_value}}},
    }

    assert migration.should_migrate(stream_state) is True
    report_state = migration.migrate(stream_state)["parent_state"]["report"]
    assert report_state["state"] == {"createTime": expected}


def test_per_partition_cursors_are_rekeyed(migration):
    """`ConcurrentPerPartitionCursor` keeps a cursor per partition under `states`.

    Re-keying only the global cursor under `state` would leave those partitions reading a field
    the cursor no longer looks for.
    """
    stream_state = {
        "state": {"date": _LEGACY_DAY},
        "parent_state": {
            "report": {
                "state": {"date": _LEGACY_DAY},
                "states": [
                    {"partition": {"id": "job-1"}, "cursor": {"date": _LEGACY_DAY}},
                    {"partition": {"id": "job-2"}, "cursor": {"date": _API_TIMESTAMP}},
                ],
            }
        },
    }

    report_state = migration.migrate(stream_state)["parent_state"]["report"]

    assert [partition_state["cursor"] for partition_state in report_state["states"]] == [
        {"createTime": _LEGACY_DAY_AS_CURSOR},
        {"createTime": _API_TIMESTAMP_AS_CURSOR},
    ]
    # Partitions are preserved, so the cursor still matches them to the parent's slices.
    assert [partition_state["partition"] for partition_state in report_state["states"]] == [{"id": "job-1"}, {"id": "job-2"}]


def test_parent_is_seeded_from_the_child_when_it_has_no_cursor(migration):
    """Through 1.3.4 the parent's cursor field did not exist on a report listing.

    So it never advanced, and plenty of connections carry no parent cursor at all. Seeding from
    the child avoids a full re-read of everything YouTube still retains on the upgrade sync.
    """
    stream_state = {"state": {"date": _LEGACY_DAY}, "parent_state": {"report": {}}}

    assert migration.should_migrate(stream_state) is True
    report_state = migration.migrate(stream_state)["parent_state"]["report"]
    assert report_state["state"] == {"createTime": _LEGACY_DAY_AS_CURSOR}


def test_lookback_window_is_preserved(migration):
    """`GlobalSubstreamCursor` measures this from how long the last sync took.

    Through 1.3.4 the migration reset it to 0 -- and because `should_migrate` was truthy for any
    low-code state, it did so on every sync, discarding the margin before it could be used.
    """
    stream_state = {
        "state": {"date": _LEGACY_DAY},
        "parent_state": {"report": {"state": {"date": _LEGACY_DAY}, "lookback_window": 1}},
    }

    assert migration.migrate(stream_state)["parent_state"]["report"]["lookback_window"] == 1


def test_unparseable_legacy_value_yields_no_cursor(migration):
    """`integration_tests/abnormal_state.json` carries `{"date": 99999999}`.

    Omitting the cursor falls back to `start_datetime` -- one wasteful full re-read, rather than
    a hard failure or an unparseable value reaching the cursor.
    """
    migrated = migration.migrate({"date": 99999999})

    assert migrated["state"] == {"date": "99999999"}
    assert "parent_state" not in migrated


@pytest.mark.parametrize(
    "stream_state, expected",
    [
        pytest.param({}, False, id="no_saved_state"),
        pytest.param({"date": 20251107}, True, id="pre_low_code"),
        pytest.param(
            {"state": {"date": _LEGACY_DAY}, "parent_state": {"report": {"state": {"date": _LEGACY_DAY}}}},
            True,
            id="parent_still_keyed_on_date",
        ),
        pytest.param(
            {"state": {"date": _LEGACY_DAY}, "parent_state": {"report": {"state": {"createTime": _API_TIMESTAMP_AS_CURSOR}}}},
            False,
            id="already_migrated",
        ),
        pytest.param(
            {"state": {"date": _LEGACY_DAY}, "parent_state": {"report": {"states": [{"partition": {}, "cursor": {"date": _LEGACY_DAY}}]}}},
            True,
            id="per_partition_still_keyed_on_date",
        ),
    ],
)
def test_should_migrate(migration, stream_state, expected):
    """`is` rather than a truthy check: through 1.3.5 this returned the saved `state` dict.

    A non-empty dict passes an `if`, so the "one-time" migration ran on every sync of every
    connection -- the mechanism behind the cursor being reset on each read.
    """
    assert migration.should_migrate(stream_state) is expected


@pytest.mark.parametrize(
    "stream_state",
    [
        pytest.param({"date": 20251107}, id="pre_low_code"),
        pytest.param(
            {"state": {"date": _LEGACY_DAY}, "parent_state": {"report": {"state": {"date": _LEGACY_DAY}, "lookback_window": 1}}},
            id="low_code",
        ),
        pytest.param(
            {"state": {"date": _LEGACY_DAY}, "parent_state": {"report": {"states": [{"partition": {}, "cursor": {"date": _LEGACY_DAY}}]}}},
            id="per_partition",
        ),
    ],
)
def test_migration_is_one_shot(migration, stream_state):
    """Migrated state must not migrate again, or the cursor is rewritten on every sync."""
    migrated = migration.migrate(stream_state)

    assert migration.should_migrate(migrated) is False
    assert migration.migrate(migrated) == migrated


def test_migrated_cursor_never_moves_forward(migration):
    """The safety argument for re-keying the cursor without a breaking change.

    A legacy value is a data day or a `startTime`; the new cursor is a `createTime`. For any
    report file `createTime > endTime > startTime >= midnight of the data day`, so reusing a
    legacy value as the `createdAfter` floor lands at or before the true `createTime`. Worst
    case is re-listing a day or two of files once; a file can never be skipped.
    """
    # The file whose data day the legacy cursor recorded, as YouTube would list it.
    file_start_time = "2025-11-07T07:00:00Z"
    file_create_time = "2025-11-09T00:00:00Z"

    for legacy_value in (_LEGACY_DAY, file_start_time):
        stream_state = {"state": {"date": _LEGACY_DAY}, "parent_state": {"report": {"state": {"date": legacy_value}}}}
        migrated_cursor = migration.migrate(stream_state)["parent_state"]["report"]["state"]["createTime"]

        # Lexicographic comparison is a real ordering here: both are zero-padded UTC ISO-8601.
        assert migrated_cursor <= migration._to_cursor_value(file_create_time)
