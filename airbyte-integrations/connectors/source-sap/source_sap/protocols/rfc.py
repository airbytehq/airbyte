"""SAP tables and CDS views over RFC (`erpl_rfc`)."""

from __future__ import annotations

import logging
import re
from collections.abc import Mapping, Sequence
from typing import Any

from source_sap.errors import config_error, traced
from source_sap.protocols.base import (
    ProtocolDriver,
    ReadPlan,
    SapObject,
    clamp,
    sql_string_literal,
)
from source_sap.retry import retry_transient
from source_sap.sap_values import MAX_STATE_VALUE, checked_state_value, sap_date, sap_time, sap_timestamp
from source_sap.session import ErplSession
from source_sap.types import json_schema_for_fields, primary_key_for_fields

logger = logging.getLogger("airbyte")


def _sql_literal(value: str) -> str:
    return sql_string_literal(str(value))


CURSOR_FIELD_PATTERN = re.compile(r"^[A-Z0-9_/]{1,30}$")

#: erpl's own default fetch budget, in bytes per round trip, read from **erpl
#: v2026.09.04**. Both the partition scaling below and the memory envelope in
#: docs/operations.md are derived from it, so a later erpl that changes its
#: default would make this connector mis-size quietly. `bin/trace-round-trips.py`
#: is the check: a serial scan's rows-per-round-trip moves if this number is
#: stale.
DEFAULT_FETCH_SIZE = 1_310_720

#: Below this many bytes per partition worker, a round trip carries so few rows
#: that the trip count dominates. A 55-column DD02L row is ~12 KB, so this floor
#: is about 40 rows per call.
MIN_BUDGET_PER_WORKER = 512 * 1024

#: Upper bound on the fetch budget. 4 MB was an arbitrary guess that turned out
#: to cap below what measurement showed to be useful: 32x the default (~42 MB)
#: gave the best throughput on a 55-column table. 64 MiB per round trip, times a
#: bounded worker count, stays within a connector container's means.
MAX_FETCH_SIZE = 64 * 1024 * 1024

#: Longest cursor value accepted back from state. SAP takes a WHERE fragment as
#: 72-character lines, so a multi-kilobyte value dumps or truncates inside SAP
#: rather than failing here. Real checkpoints are short -- a DATS value is 8
#: characters -- so this is generous for anything legitimate.
#: Kept as the RFC-local name for the shared bound.
MAX_CURSOR_VALUE = MAX_STATE_VALUE


def sap_cursor_literal(value: Any, sap_type: str | None) -> str:
    """Render a state value as the ABAP literal SAP expects.

    State travels as JSON, so a DATS column checkpoints as "2026-09-05" -- and
    SAP rejects that with *"'2026-09-05' is not a valid value for D(8,0)"*.
    Dates, times and timestamps have to go back to their compact DDIC form.

    Raises `ValueError` for a value that is not of the column's DDIC type.
    """
    text = str(value)
    kind = (sap_type or "").strip().upper()
    # Parse and reject rather than slice. Slicing turned a DATS state of
    # "20260905120000" into "20260905" and sent SAP a selection the state never
    # described, with nothing to show for it in the logs.
    if kind == "DATS":
        return sap_date(text).replace("-", "")
    if kind == "TIMS":
        return sap_time(text).replace(":", "")
    if kind in ("UTCLONG", "UTCL", "UTCS", "UTCM", "TIMESTAMP"):
        return "".join(c for c in sap_timestamp(text) if c.isdigit())
    return text


class RfcDriver(ProtocolDriver):
    mode = "rfc"
    required_extensions = ("erpl_rfc",)

    def partitions_for(self, obj: SapObject) -> int:
        """Effective partition count for a stream, object setting winning."""
        override = self._object_overrides().get(obj.name, {})
        return clamp(override.get("partitions", self.options.get("partitions")), 0, 64) or 0

    def validate_cursor_field(self, cursor_field: str, known_fields: Sequence[str]) -> str:
        """The cursor field is interpolated bare into the ABAP WHERE fragment.

        Every other fragment goes through `sql_string_literal`; an identifier
        cannot, so it is checked against the shape SAP allows *and* against the
        fields the table actually has.
        """
        candidate = str(cursor_field).strip().upper()
        if not CURSOR_FIELD_PATTERN.match(candidate):
            raise config_error(
                f"cursor_field {cursor_field!r} is not a valid SAP field name. It must be "
                "1-30 characters of A-Z, 0-9, underscore and slash."
            )
        if candidate not in {str(f).upper() for f in known_fields}:
            raise config_error(
                f"cursor_field {cursor_field!r} is not a field of this table. Available "
                f"fields: {', '.join(sorted(str(f) for f in known_fields))}."
            )
        return candidate

    # ---- discovery ------------------------------------------------------------

    @retry_transient()
    def check(self, session: ErplSession) -> str:
        try:
            result = session.cursor().execute("PRAGMA sap_rfc_ping").fetchone()
        except Exception as exc:
            raise traced("SAP RFC connection test failed", exc) from exc
        return f"Connected to SAP via RFC ({result[0] if result else 'ok'})."

    def discover(self, session: ErplSession) -> list[SapObject]:
        names = self._selected_table_names(session)
        cursor = session.cursor()
        objects: list[SapObject] = []
        for name in names:
            try:
                rows = cursor.execute(
                    f"SELECT pos, is_key, field, text, sap_type, length, decimals "
                    f"FROM sap_describe_fields({_sql_literal(name)}) ORDER BY pos"
                ).fetchall()
            except Exception as exc:
                logger.warning("Skipping %s: could not read its field list (%s)", name, exc)
                continue
            if not rows:
                logger.warning("Skipping %s: SAP reported no fields.", name)
                continue
            fields = [
                {
                    "technical_name": row[2],
                    "text": row[3],
                    "abap_type": row[4],
                    "length": int(row[5] or 0),
                    "decimals": int(row[6] or 0),
                    "key": row[1] in (True, "X", "x"),
                }
                for row in rows
            ]
            override = self._object_overrides().get(name, {})
            cursor_field = override.get("cursor_field")
            if cursor_field:
                cursor_field = self.validate_cursor_field(cursor_field, [f["technical_name"] for f in fields])
            cursor_sap_type = next((f["abap_type"] for f in fields if f["technical_name"] == cursor_field), None)
            # SAP's own key is right most of the time, but a CDS view can
            # report none, so a configured key wins.
            configured_key = override.get("primary_key")
            primary_key = [[k] for k in configured_key] if configured_key else primary_key_for_fields(fields)
            objects.append(
                SapObject(
                    name=name,
                    json_schema=json_schema_for_fields(fields),
                    primary_key=primary_key,
                    supports_incremental=bool(cursor_field),
                    meta={
                        "table": name,
                        "cursor_field": cursor_field,
                        "cursor_sap_type": cursor_sap_type,
                    },
                )
            )
        return objects

    def _selected_table_names(self, session: ErplSession) -> list[str]:
        overrides = self._object_overrides()
        pattern = (self.options.get("table_pattern") or "").strip()
        if not pattern and not overrides:
            raise config_error(
                "No SAP tables selected. Set 'table_pattern' (for example '/DMO/*' or 'SFLIGHT') "
                "and/or list tables explicitly under 'objects'."
            )
        names: list[str] = []
        if pattern:
            try:
                rows = (
                    session.cursor()
                    .execute("SELECT table_name FROM sap_show_tables(TABLENAME := ?) ORDER BY 1", [pattern])
                    .fetchall()
                )
            except Exception as exc:
                raise traced(f"Could not list SAP tables matching {pattern!r}", exc) from exc
            names.extend(row[0] for row in rows)
        for name in overrides:
            if name not in names:
                names.append(name)
        if not names:
            raise config_error(
                f"No SAP table matched the pattern {pattern!r}. Patterns use SAP wildcards "
                "('*' for any sequence of characters), and the name is case-sensitive."
            )
        return names

    # ---- reading --------------------------------------------------------------

    def read_plans(
        self, session: ErplSession, obj: SapObject, *, incremental: bool, state: Mapping[str, Any]
    ) -> list[ReadPlan]:
        table = str(obj.meta.get("table") or obj.name)
        override = self._object_overrides().get(obj.name, {})
        args: list[str] = [_sql_literal(table)]

        columns = override.get("columns") or self.options.get("columns")
        if columns:
            rendered = ", ".join(_sql_literal(c) for c in columns)
            args.append(f"COLUMNS := [{rendered}]")

        partitions = self.partitions_for(obj)

        predicates: list[str] = []
        user_filter = (override.get("filter") or "").strip()
        if user_filter:
            predicates.append(user_filter)

        cursor_field = obj.meta.get("cursor_field") or override.get("cursor_field")
        if incremental and cursor_field:
            # Checked here as well as at discovery: this is the sink -- the name
            # is interpolated bare into the ABAP fragment, because an identifier
            # cannot go through `sql_string_literal` -- and the fallback above
            # reads a config value discovery may never have seen.
            checked_field = str(cursor_field).strip().upper()
            if not CURSOR_FIELD_PATTERN.match(checked_field):
                raise config_error(
                    f"cursor_field {cursor_field!r} is not a valid SAP field name. It must be "
                    "1-30 characters of A-Z, 0-9, underscore and slash."
                )
            since = state.get(str(cursor_field))
            if since not in (None, ""):
                checked_state_value(str(cursor_field), since)
                try:
                    literal = sap_cursor_literal(since, obj.meta.get("cursor_sap_type"))
                except ValueError as exc:
                    raise ValueError(
                        f"The state value for {cursor_field} is not usable as a SAP "
                        f"{obj.meta.get('cursor_sap_type')} value: {exc}. Reset the stream's state."
                    ) from exc
                # SAP's WHERE fragment uses ABAP literal quoting, and the whole
                # fragment is then a DuckDB string literal -- hence two levels.
                predicates.append(f"{checked_field} >= {_sql_literal(literal)}")
        if predicates:
            combined = " AND ".join(f"( {p} )" for p in predicates) if len(predicates) > 1 else predicates[0]
            args.append(f"FILTER := {_sql_literal(combined)}")

        # Stated unconditionally so one number governs the query.
        args.append(f"PARTITIONS := {partitions}")

        # erpl divides its fetch budget across partition workers, and the budget
        # is bytes rather than rows, so on a wide table each worker is starved.
        # Measured on a 55-column, 164,673-row table: a serial scan gets ~107
        # rows per RFC round trip, eight partitions with the default budget get
        # ~17, and the round-trip count goes up 6.3x. Multiplying the budget by
        # the worker count restores ~94 rows per call -- most of the serial
        # figure -- so asking for partitions is taken as asking for the budget to
        # keep up. (A 32x budget reached ~187, better still, but that is four
        # times the memory per worker for the remaining 13%, and the end-to-end
        # figure does not move with it.)
        #
        # This removes one penalty, not all of them: measured end to end, a
        # partitioned read is still slower through this connector than a serial
        # one even with the budget scaled, and why is not established. Hence
        # `partitions` defaults to 0. See docs/performance.md.
        configured = override.get("fetch_size", self.options.get("fetch_size"))
        # A configured 0 means "I did not set this", not "one byte" -- which is
        # what clamping it into the valid range would otherwise make of it.
        fetch_size = clamp(configured, 1, MAX_FETCH_SIZE) if configured else None
        if fetch_size is None and partitions:
            fetch_size = min(DEFAULT_FETCH_SIZE * partitions, MAX_FETCH_SIZE)
        elif fetch_size is not None and partitions and fetch_size // partitions < MIN_BUDGET_PER_WORKER:
            logger.warning(
                "%s: fetch_size %d split across %d partitions leaves %d bytes per "
                "worker, below %d. Each RFC round trip will then carry very few "
                "rows. Raise fetch_size, or lower partitions.",
                obj.name,
                fetch_size,
                partitions,
                fetch_size // partitions,
                MIN_BUDGET_PER_WORKER,
            )
        if fetch_size is not None:
            args.append(f"FETCH_SIZE := {fetch_size}")

        for cfg_key, sql_key, low, high in (
            ("threads", "THREADS", 0, 32),
            ("max_rows", "MAX_ROWS", 0, 2_147_483_647),
        ):
            value = clamp(override.get(cfg_key, self.options.get(cfg_key)), low, high)
            if value is not None:
                args.append(f"{sql_key} := {value}")

        sql = f"SELECT * FROM sap_read_table({', '.join(args)})"
        return [ReadPlan(sql=sql, slice_={"table": table})]

    def next_state(self, session: ErplSession, obj: SapObject, previous: Mapping[str, Any]) -> Mapping[str, Any]:
        # The cursor value is observed from the records themselves; see cursors.py.
        return dict(previous)

    def cursor_field(self, obj: SapObject) -> str | None:
        value = obj.meta.get("cursor_field")
        return str(value) if value else None
