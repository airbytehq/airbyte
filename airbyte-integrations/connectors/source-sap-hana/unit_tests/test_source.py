# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any

import pytest
from source_sap_hana import SourceSapHana

from airbyte_cdk.models import (
    AirbyteStateBlob,
    AirbyteStateMessage,
    AirbyteStateType,
    AirbyteStreamState,
    AirbyteStreamStatus,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    Status,
    StreamDescriptor,
    SyncMode,
    Type,
)
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


ACDOCA_COLUMNS = [("RCLNT", "NVARCHAR"), ("BELNR", "NVARCHAR"), ("DOCLN", "NVARCHAR"), ("HSL", "DECIMAL"), ("TIMESTAMP", "DECIMAL")]
ACDOCA_ROWS = [
    ("100", "0000000001", "000001", -150.25, 20260101),
    ("100", "0000000001", "000002", 150.25, 20260101),
    ("100", "0000000002", "000001", -10.0, 20260102),
    ("100", "0000000003", "000001", 99.99, 20260103),
    ("100", "0000000004", "000001", 1.0, 20260103),
    ("100", "0000000005", "000001", 2.0, 20260104),
]


@pytest.fixture
def seeded(hana):
    hana.add_table("ACDOCA", ACDOCA_COLUMNS, ACDOCA_ROWS, pk=["RCLNT", "BELNR", "DOCLN"])
    hana.add_table("MAKT", [("MATNR", "NVARCHAR"), ("MAKTX", "NVARCHAR")], [("M1", "Libro\x00 A"), ("M2", "Libro B")])
    hana.add_table("ZV_SALES", [("ID", "INTEGER")], [(1,)], view=True)
    return hana


def configured_catalog(source, config, logger, names, sync_mode=SyncMode.full_refresh, cursor=None):
    streams = {s.name: s for s in source.discover(logger, config).streams}
    return ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=streams[name],
                sync_mode=sync_mode,
                destination_sync_mode=DestinationSyncMode.append,
                cursor_field=cursor,
            )
            for name in names
        ]
    )


def state_for(name: str, data: dict[str, Any]) -> list[AirbyteStateMessage]:
    return [
        AirbyteStateMessage(
            type=AirbyteStateType.STREAM,
            stream=AirbyteStreamState(
                stream_descriptor=StreamDescriptor(name=name, namespace="SAPHANADB"),
                stream_state=AirbyteStateBlob(**data),
            ),
        )
    ]


def split(messages):
    messages = list(messages)
    records = [m.record.data for m in messages if m.type == Type.RECORD]
    states = [dict(m.state.stream.stream_state.__dict__) for m in messages if m.type == Type.STATE]
    statuses = [m.trace.stream_status.status for m in messages if m.type == Type.TRACE and m.trace.stream_status]
    return records, states, statuses


# ------------------------------------------------------------------------ check


def test_check_succeeds(seeded, config, logger):
    assert SourceSapHana().check(logger, config).status == Status.SUCCEEDED


def test_check_reports_missing_schema(seeded, config, logger):
    config["schemas"] = ["SAPHANADB", "NOPE"]
    status = SourceSapHana().check(logger, config)
    assert status.status == Status.FAILED
    assert "NOPE" in status.message


def test_check_reports_connection_error(hana, config, logger):
    config["max_retries"] = 0
    hana.fail_on_connect = 1
    status = SourceSapHana().check(logger, config)
    assert status.status == Status.FAILED
    assert "-10709" in status.message


# --------------------------------------------------------------------- discover


def test_discover(seeded, config, logger):
    streams = {s.name: s for s in SourceSapHana().discover(logger, config).streams}
    assert set(streams) == {"ACDOCA", "MAKT"}  # views excluded by default
    acdoca = streams["ACDOCA"]
    assert acdoca.namespace == "SAPHANADB"
    assert list(acdoca.json_schema["properties"]) == [c for c, _ in ACDOCA_COLUMNS]
    assert acdoca.json_schema["properties"]["HSL"] == {"type": ["null", "number"]}
    assert acdoca.source_defined_primary_key == [["RCLNT"], ["BELNR"], ["DOCLN"]]
    assert streams["MAKT"].source_defined_primary_key is None
    assert {m.value for m in acdoca.supported_sync_modes} == {"full_refresh", "incremental"}


def test_discover_fails_on_missing_schema(seeded, config, logger):
    config["schemas"] = ["NOPE"]
    with pytest.raises(AirbyteTracedException, match="NOPE"):
        SourceSapHana().discover(logger, config)


def test_discover_with_views_and_patterns(seeded, config, logger):
    config.update(include_views=True, table_name_patterns=["ACD%", "ZV_%"])
    names = {s.name for s in SourceSapHana().discover(logger, config).streams}
    assert names == {"ACDOCA", "ZV_SALES"}


# ------------------------------------------------------------------------- read


def test_full_refresh(seeded, config, logger):
    source = SourceSapHana()
    catalog = configured_catalog(source, config, logger, ["MAKT"])
    records, states, statuses = split(source.read(logger, config, catalog, []))
    assert records == [{"MATNR": "M1", "MAKTX": "Libro A"}, {"MATNR": "M2", "MAKTX": "Libro B"}]
    assert states == [{"__ab_no_cursor_state_message": True}]
    assert statuses == [AirbyteStreamStatus.STARTED, AirbyteStreamStatus.RUNNING, AirbyteStreamStatus.COMPLETE]


def test_full_refresh_respects_column_selection(seeded, config, logger):
    config["resumable_full_refresh"] = False
    source = SourceSapHana()
    catalog = configured_catalog(source, config, logger, ["ACDOCA"])
    catalog.streams[0].stream.json_schema["properties"] = {"BELNR": {}, "HSL": {}}
    records, _, _ = split(source.read(logger, config, catalog, []))
    assert records[0] == {"BELNR": "0000000001", "HSL": -150.25}


def test_full_refresh_retries_when_connection_drops_before_first_record(seeded, config, logger):
    seeded.fail_after_rows = [0]
    source = SourceSapHana()
    catalog = configured_catalog(source, config, logger, ["MAKT"])
    records, _, statuses = split(source.read(logger, config, catalog, []))
    assert len(records) == 2
    assert statuses[-1] == AirbyteStreamStatus.COMPLETE


def test_full_refresh_fails_stream_when_connection_drops_mid_stream(seeded, config, logger):
    config["resumable_full_refresh"] = False
    seeded.fail_after_rows = [3]
    source = SourceSapHana()
    catalog = configured_catalog(source, config, logger, ["ACDOCA", "MAKT"])
    messages = []
    with pytest.raises(AirbyteTracedException, match="SAPHANADB.ACDOCA"):
        for m in source.read(logger, config, catalog, []):
            messages.append(m)
    records, _, statuses = split(messages)
    # ACDOCA is marked incomplete, but MAKT is still synced.
    assert AirbyteStreamStatus.INCOMPLETE in statuses
    assert statuses[-1] == AirbyteStreamStatus.COMPLETE
    assert {"MATNR": "M2", "MAKTX": "Libro B"} in records


def test_incremental_initial_sync(seeded, config, logger):
    source = SourceSapHana()
    catalog = configured_catalog(source, config, logger, ["ACDOCA"], SyncMode.incremental, ["TIMESTAMP"])
    records, states, _ = split(source.read(logger, config, catalog, []))
    assert len(records) == 6
    # A checkpoint is emitted only once every row of a cursor value has been emitted.
    assert [s["cursor"] for s in states] == [20260101, 20260102, 20260103, 20260104]
    assert all(s["cursor_field"] == "TIMESTAMP" for s in states)


def test_incremental_from_state(seeded, config, logger):
    source = SourceSapHana()
    catalog = configured_catalog(source, config, logger, ["ACDOCA"], SyncMode.incremental, ["TIMESTAMP"])
    state = state_for("ACDOCA", {"cursor_field": "TIMESTAMP", "cursor": 20260102})
    records, states, _ = split(source.read(logger, config, catalog, state))
    assert [r["BELNR"] for r in records] == ["0000000003", "0000000004", "0000000005"]
    assert states[-1]["cursor"] == 20260104
    sql, params = seeded.executed[-1]
    assert '"TIMESTAMP" > ?' in sql and params == [20260102]


def test_incremental_no_new_rows_keeps_state(seeded, config, logger):
    source = SourceSapHana()
    catalog = configured_catalog(source, config, logger, ["ACDOCA"], SyncMode.incremental, ["TIMESTAMP"])
    state = state_for("ACDOCA", {"cursor_field": "TIMESTAMP", "cursor": 20260104})
    records, states, _ = split(source.read(logger, config, catalog, state))
    assert records == []
    assert states == [{"cursor_field": "TIMESTAMP", "cursor": 20260104}]


def test_incremental_resumes_after_connection_drop(seeded, config, logger):
    # Drop after 4 rows: rows 1-4 emitted (cursor 0101, 0101, 0102, 0103), 0102 is the last complete value.
    seeded.fail_after_rows = [4]
    source = SourceSapHana()
    catalog = configured_catalog(source, config, logger, ["ACDOCA"], SyncMode.incremental, ["TIMESTAMP"])
    records, states, statuses = split(source.read(logger, config, catalog, []))
    assert statuses[-1] == AirbyteStreamStatus.COMPLETE
    sql, params = seeded.executed[-1]
    assert params == [20260102]  # resumed from the last fully emitted cursor value
    # At-least-once: only the partially emitted cursor value (20260103) is re-read.
    belnrs = [r["BELNR"] for r in records]
    assert belnrs == ["0000000001", "0000000001", "0000000002", "0000000003", "0000000003", "0000000004", "0000000005"]
    assert states[-1]["cursor"] == 20260104


def test_incremental_gives_up_after_max_retries(seeded, config, logger):
    config["max_retries"] = 1
    seeded.fail_after_rows = [0, 0]
    source = SourceSapHana()
    catalog = configured_catalog(source, config, logger, ["ACDOCA"], SyncMode.incremental, ["TIMESTAMP"])
    with pytest.raises(AirbyteTracedException):
        list(source.read(logger, config, catalog, []))


def test_incremental_ignores_state_for_other_cursor(seeded, config, logger):
    source = SourceSapHana()
    catalog = configured_catalog(source, config, logger, ["ACDOCA"], SyncMode.incremental, ["TIMESTAMP"])
    state = state_for("ACDOCA", {"cursor_field": "BELNR", "cursor": "0000000004"})
    records, _, _ = split(source.read(logger, config, catalog, state))
    assert len(records) == 6


def test_incremental_rejects_unknown_cursor(seeded, config, logger):
    source = SourceSapHana()
    catalog = configured_catalog(source, config, logger, ["ACDOCA"], SyncMode.incremental, ["NOPE"])
    with pytest.raises(AirbyteTracedException):
        list(source.read(logger, config, catalog, []))


def test_spec_is_valid(logger):
    spec = SourceSapHana().spec(logger)
    assert spec.connectionSpecification["properties"]["password"]["airbyte_secret"] is True


# ------------------------------------------------------- resumable full refresh


def acdoca_keys(records):
    return [(r["RCLNT"], r["BELNR"], r["DOCLN"]) for r in records]


ALL_KEYS = [(r[0], r[1], r[2]) for r in ACDOCA_ROWS]


def test_discover_marks_tables_with_primary_key_resumable(seeded, config, logger):
    streams = {s.name: s for s in SourceSapHana().discover(logger, config).streams}
    assert streams["ACDOCA"].is_resumable is True
    assert streams["MAKT"].is_resumable is False
    config["resumable_full_refresh"] = False
    streams = {s.name: s for s in SourceSapHana().discover(logger, config).streams}
    assert streams["ACDOCA"].is_resumable is False


def test_resumable_full_refresh_pages_by_primary_key(seeded, config, logger):
    config["full_refresh_page_size"] = 4
    source = SourceSapHana()
    catalog = configured_catalog(source, config, logger, ["ACDOCA"])
    records, states, statuses = split(source.read(logger, config, catalog, []))
    assert acdoca_keys(records) == sorted(ALL_KEYS)
    assert states == [
        {"primary_key": {"RCLNT": "100", "BELNR": "0000000003", "DOCLN": "000001"}},
        {"primary_key": {"RCLNT": "100", "BELNR": "0000000005", "DOCLN": "000001"}},
        {"__ab_full_refresh_sync_complete": True},
    ]
    assert statuses[-1] == AirbyteStreamStatus.COMPLETE
    sql, params = seeded.executed[-1]
    assert sql.endswith('ORDER BY "RCLNT", "BELNR", "DOCLN" LIMIT 4')
    assert params == ["100", "100", "0000000003", "100", "0000000003", "000001"]


def test_resumable_full_refresh_stops_on_exact_multiple_of_page_size(seeded, config, logger):
    config["full_refresh_page_size"] = 3
    source = SourceSapHana()
    catalog = configured_catalog(source, config, logger, ["ACDOCA"])
    records, states, _ = split(source.read(logger, config, catalog, []))
    assert acdoca_keys(records) == sorted(ALL_KEYS)
    assert states[-1] == {"__ab_full_refresh_sync_complete": True}
    assert len(states) == 3  # two full pages + completion (the third, empty page emits no checkpoint)


def test_resumable_full_refresh_resumes_after_connection_drop_without_duplicates(seeded, config, logger):
    config["full_refresh_page_size"] = 100
    seeded.fail_after_rows = [3]
    source = SourceSapHana()
    catalog = configured_catalog(source, config, logger, ["ACDOCA"])
    records, states, statuses = split(source.read(logger, config, catalog, []))
    assert acdoca_keys(records) == sorted(ALL_KEYS)  # every row exactly once
    assert states[0] == {"primary_key": {"RCLNT": "100", "BELNR": "0000000002", "DOCLN": "000001"}}
    assert statuses[-1] == AirbyteStreamStatus.COMPLETE


def test_resumable_full_refresh_resumes_from_previous_attempt_state(seeded, config, logger):
    source = SourceSapHana()
    catalog = configured_catalog(source, config, logger, ["ACDOCA"])
    state = state_for("ACDOCA", {"primary_key": {"RCLNT": "100", "BELNR": "0000000003", "DOCLN": "000001"}})
    records, _, _ = split(source.read(logger, config, catalog, state))
    assert acdoca_keys(records) == [("100", "0000000004", "000001"), ("100", "0000000005", "000001")]


def test_resumable_full_refresh_restarts_after_completed_sync(seeded, config, logger):
    source = SourceSapHana()
    catalog = configured_catalog(source, config, logger, ["ACDOCA"])
    state = state_for("ACDOCA", {"__ab_full_refresh_sync_complete": True})
    records, _, _ = split(source.read(logger, config, catalog, state))
    assert len(records) == len(ACDOCA_ROWS)


def test_resumable_full_refresh_always_emits_primary_key_columns(seeded, config, logger):
    source = SourceSapHana()
    catalog = configured_catalog(source, config, logger, ["ACDOCA"])
    catalog.streams[0].stream.json_schema["properties"] = {"HSL": {}}
    records, _, _ = split(source.read(logger, config, catalog, []))
    assert set(records[0]) == {"HSL", "RCLNT", "BELNR", "DOCLN"}


# ---------------------------------------------------------------- stream filters


def test_stream_filter_applies_to_full_refresh(seeded, config, logger):
    config["stream_settings"] = [{"stream": "MAKT", "condition": "MATNR = 'M2'"}]
    source = SourceSapHana()
    catalog = configured_catalog(source, config, logger, ["MAKT"])
    records, _, _ = split(source.read(logger, config, catalog, []))
    assert records == [{"MATNR": "M2", "MAKTX": "Libro B"}]


def test_stream_filter_combines_with_keyset_predicate(seeded, config, logger):
    config.update(full_refresh_page_size=1, stream_settings=[{"stream": "SAPHANADB.ACDOCA", "condition": "HSL > 0 OR HSL < -100"}])
    source = SourceSapHana()
    catalog = configured_catalog(source, config, logger, ["ACDOCA"])
    records, _, _ = split(source.read(logger, config, catalog, []))
    assert [r["HSL"] for r in records] == [-150.25, 150.25, 99.99, 1.0, 2.0]
    sql, _ = seeded.executed[-1]
    assert "WHERE (HSL > 0 OR HSL < -100) AND ((" in sql  # the user filter is parenthesised before AND


def test_stream_filter_applies_to_incremental(seeded, config, logger):
    config["stream_settings"] = [{"stream": "ACDOCA", "condition": "BELNR <> '0000000004'"}]
    source = SourceSapHana()
    catalog = configured_catalog(source, config, logger, ["ACDOCA"], SyncMode.incremental, ["TIMESTAMP"])
    state = state_for("ACDOCA", {"cursor_field": "TIMESTAMP", "cursor": 20260102})
    records, _, _ = split(source.read(logger, config, catalog, state))
    assert [r["BELNR"] for r in records] == ["0000000003", "0000000005"]


def test_incremental_without_cursor_falls_back_to_full_refresh(seeded, config, logger):
    source = SourceSapHana()
    catalog = configured_catalog(source, config, logger, ["ACDOCA", "MAKT"], SyncMode.incremental, cursor=None)
    records, states, statuses = split(source.read(logger, config, catalog, []))
    assert len(records) == len(ACDOCA_ROWS) + 2
    assert {"__ab_full_refresh_sync_complete": True} in states  # ACDOCA: keyset full refresh
    assert {"__ab_no_cursor_state_message": True} in states  # MAKT: plain full refresh
    assert statuses.count(AirbyteStreamStatus.COMPLETE) == 2


# ---------------------------------------------------------- stream settings


def test_primary_key_override_makes_table_dedupable_and_resumable(seeded, config, logger):
    config.update(full_refresh_page_size=1, stream_settings=[{"stream": "MAKT", "primary_key": ["MATNR"]}])
    source = SourceSapHana()
    streams = {s.name: s for s in source.discover(logger, config).streams}
    assert streams["MAKT"].source_defined_primary_key == [["MATNR"]]
    assert streams["MAKT"].is_resumable is True
    catalog = configured_catalog(source, config, logger, ["MAKT"])
    records, states, _ = split(source.read(logger, config, catalog, []))
    assert [r["MATNR"] for r in records] == ["M1", "M2"]
    assert states[-1] == {"__ab_full_refresh_sync_complete": True}
    assert {"primary_key": {"MATNR": "M2"}} in states


def test_default_cursor_field_is_discovered_and_used(seeded, config, logger):
    config["stream_settings"] = [{"stream": "ACDOCA", "cursor_field": "TIMESTAMP"}]
    source = SourceSapHana()
    streams = {s.name: s for s in source.discover(logger, config).streams}
    assert streams["ACDOCA"].default_cursor_field == ["TIMESTAMP"]
    assert streams["MAKT"].default_cursor_field is None
    catalog = configured_catalog(source, config, logger, ["ACDOCA"], SyncMode.incremental, cursor=None)
    _, states, _ = split(source.read(logger, config, catalog, []))
    assert states[-1] == {"cursor_field": "TIMESTAMP", "cursor": 20260104}


def test_user_selected_cursor_wins_over_default(seeded, config, logger):
    config["stream_settings"] = [{"stream": "ACDOCA", "cursor_field": "TIMESTAMP"}]
    source = SourceSapHana()
    catalog = configured_catalog(source, config, logger, ["ACDOCA"], SyncMode.incremental, cursor=["BELNR"])
    _, states, _ = split(source.read(logger, config, catalog, []))
    assert states[-1] == {"cursor_field": "BELNR", "cursor": "0000000005"}


def test_stream_settings_with_unknown_column_is_a_config_error(seeded, config, logger):
    config["stream_settings"] = [{"stream": "ACDOCA", "primary_key": ["NOPE"]}]
    with pytest.raises(AirbyteTracedException, match="NOPE"):
        SourceSapHana().discover(logger, config)


# ------------------------------------------------ estimates and check-time validation


def estimates(messages):
    return {m.trace.estimate.name: m.trace.estimate.row_estimate for m in messages if m.type == Type.TRACE and m.trace.estimate is not None}


def test_full_refresh_emits_row_estimate(seeded, config, logger):
    source = SourceSapHana()
    catalog = configured_catalog(source, config, logger, ["ACDOCA", "MAKT"])
    assert estimates(source.read(logger, config, catalog, [])) == {"ACDOCA": 6, "MAKT": 2}


def test_no_estimate_for_filtered_or_incremental_streams(seeded, config, logger):
    config["stream_settings"] = [{"stream": "MAKT", "condition": "MATNR = 'M1'"}]
    source = SourceSapHana()
    catalog = configured_catalog(source, config, logger, ["MAKT"])
    catalog.streams += configured_catalog(source, config, logger, ["ACDOCA"], SyncMode.incremental, ["TIMESTAMP"]).streams
    assert estimates(source.read(logger, config, catalog, [])) == {}


def test_check_validates_stream_conditions(seeded, config, logger):
    config["stream_settings"] = [
        {"stream": "ACDOCA", "condition": "NOPE_COLUMN = 1"},
        {"stream": "MAKT", "condition": "MATNR = 'M1' AND"},
        {"stream": "GHOST", "condition": "1 = 1"},
        {"stream": "SAPHANADB.MARA_MISSING", "cursor_field": "X"},
    ]
    status = SourceSapHana().check(logger, config)
    assert status.status == Status.FAILED
    assert "ACDOCA: [260]" in status.message
    assert "MAKT: [257]" in status.message
    assert "GHOST: table or view not found" in status.message
    assert "SAPHANADB.MARA_MISSING: table or view not found" in status.message


def test_check_accepts_valid_stream_conditions(seeded, config, logger):
    config["stream_settings"] = [{"stream": "ACDOCA", "condition": "RCLNT = '100' AND HSL > 0", "cursor_field": "TIMESTAMP"}]
    assert SourceSapHana().check(logger, config).status == Status.SUCCEEDED
