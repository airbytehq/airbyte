"""SAP BW cubes and BEx queries over BICS (`erpl_bics`).

BICS is a *stateful* protocol: open a session, configure axes and filters, then
fetch.  And it cannot paginate -- BW materialises the entire result set or none
of it -- so the only way to bound memory on a large cube is to slice the query
yourself on a characteristic.  Each slice is a separate BICS session, which is
what makes slices independently readable.
"""

from __future__ import annotations

import hashlib
import logging
import re
from collections.abc import Mapping, Sequence
from typing import Any

from source_sap.duck import schema_from_description
from source_sap.errors import config_error, traced
from source_sap.protocols.base import ProtocolDriver, ReadPlan, SapObject, sql_string_literal
from source_sap.retry import retry_transient
from source_sap.sap_values import checked_state_value
from source_sap.session import ErplSession

logger = logging.getLogger("airbyte")

# BW appends a grand-total row to every result; it is not a fact and must not
# be emitted as one.
_TOTAL_LABELS = {
    "SUMME",
    "GESAMTERGEBNIS",
    "OVERALL RESULT",
    "RESULT",
    "ERGEBNIS",
    "TOTAL",
    "GESAMT",
}


def _lit(value: Any) -> str:
    return sql_string_literal(str(value))


def is_grand_total_row(record: Mapping[str, Any], row_axis_fields: Sequence[str] | None = None) -> bool:
    """True when a BICS row is BW's grand total rather than a data row.

    When the row axis is known, only those columns are examined -- a key figure
    that happens to read "Result" must not drop the row. When it is not (no
    `rows` configured), every string column is checked, because emitting the
    total as a fact is worse than the small chance of dropping a real row whose
    characteristic value is literally "Overall Result".
    """
    fields = list(row_axis_fields) if row_axis_fields else list(record)
    for field in fields:
        value = record.get(field)
        if isinstance(value, str) and value.strip().upper() in _TOTAL_LABELS:
            return True
    return False


_MAX_SESSION_ID = 40
_SESSION_PREFIX = "abyte_"


def session_id_for(stream_name: str, suffix: str = "") -> str:
    """A distinct BICS session id per stream, and per slice within a stream.

    The discriminator is budgeted *before* truncation. Appending it and then
    truncating -- which is the obvious way to write this -- silently gives every
    slice of a long-named BW query the same id, and the Concurrent CDK reads
    slices in parallel, so their sessions would interleave on the server.
    """
    digest = hashlib.sha1(f"{stream_name}|{suffix}".encode()).hexdigest()[:8]
    readable = re.sub(r"[^A-Za-z0-9]+", "_", stream_name).strip("_").lower()
    budget = _MAX_SESSION_ID - len(_SESSION_PREFIX) - len(digest) - 1
    return f"{_SESSION_PREFIX}{readable[:budget]}_{digest}"


class BicsDriver(ProtocolDriver):
    mode = "bics"
    required_extensions = ("erpl_rfc", "erpl_bics")

    # ---- discovery ------------------------------------------------------------

    @retry_transient()
    def check(self, session: ErplSession) -> str:
        cursor = session.cursor()
        try:
            cursor.execute("PRAGMA sap_rfc_ping").fetchone()
            rows = cursor.execute("SELECT count(*) FROM sap_bics_show_cubes()").fetchone()
        except Exception as exc:
            raise traced("SAP BICS connection test failed", exc) from exc
        return f"Connected to SAP BW via BICS ({rows[0] if rows else 0} InfoProviders visible)."

    def discover(self, session: ErplSession) -> list[SapObject]:
        self.check_incremental_config()
        cursor = session.cursor()
        objects: list[SapObject] = []
        for name, override in self._selected(session).items():
            cube = str(override.get("cube") or override.get("query") or name)
            try:
                schema = self._describe(cursor, name, override, cube)
            except Exception as exc:
                logger.warning("Skipping BICS object %s: %s", name, exc)
                continue
            if schema is None:
                continue
            objects.append(
                SapObject(
                    name=name,
                    json_schema=schema,
                    primary_key=[[k] for k in (override.get("primary_key") or [])] or None,
                    supports_incremental=self.supports_incremental(override),
                    meta={
                        "cube": cube,
                        "query": override.get("query"),
                        "session_id": session_id_for(name),
                        "row_axis": list(override.get("rows") or []),
                        "cursor_variable": override.get("cursor_variable"),
                        "cursor_field": override.get("cursor_field"),
                    },
                )
            )
        return objects

    def _describe(self, cursor: Any, name: str, override: Mapping[str, Any], cube: str) -> dict[str, Any] | None:
        """Open a DESCRIBE session and read the result columns."""
        self._assert_mandatory_variables_bound(cursor, override, cube)
        obj = SapObject(
            name=name,
            json_schema={},
            meta={
                "cube": cube,
                "query": override.get("query"),
                "session_id": session_id_for(name, "d"),
            },
        )
        statements = self.session_statements(obj)
        for statement in statements:
            cursor.execute(statement)
        schema = schema_from_description(cursor.description)
        return schema if schema["properties"] else None

    def _assert_mandatory_variables_bound(self, cursor: Any, override: Mapping[str, Any], cube: str) -> None:
        """BW refuses to produce a result while a mandatory BEx variable is unbound."""
        query = override.get("query")
        if not query:
            return
        if override.get("variant"):
            # A variant fills the query's variables on the BW side. Which ones it
            # fills is not visible from here, so nothing can be called missing.
            return
        bound = {str(v.get("name", "")).upper() for v in (override.get("variables") or [])}
        try:
            rows = cursor.execute(
                f"SELECT name, mandatory, input_enabled FROM sap_bics_variables({_lit(cube)}, query := {_lit(query)})"
            ).fetchall()
        except Exception as exc:
            # Best-effort, not a gate: BW does not enumerate variables for every
            # query, and refusing those would break configurations that work.
            # Said aloud, because the alternative is a promise that silently
            # did not apply -- and the symptom is a green sync returning nothing.
            logger.warning(
                "Could not check the mandatory BEx variables of %s (%s). If the sync "
                "returns no rows, an unbound mandatory variable is the first thing to "
                "check in RSRT.",
                query,
                str(exc).splitlines()[0] if str(exc) else exc,
            )
            return
        missing = [r[0] for r in rows if r[1] and r[2] and str(r[0]).upper() not in bound]
        if missing:
            raise config_error(
                f"BEx query {query!r} has mandatory variables that are not bound: "
                f"{', '.join(missing)}. Add them to the object's 'variables' list."
            )

    def _selected(self, session: ErplSession) -> dict[str, Mapping[str, Any]]:
        overrides = dict(self._object_overrides())
        pattern = (self.options.get("query_pattern") or "").strip()
        if pattern:
            obj_type = (self.options.get("object_type") or "QUERY").upper()
            try:
                rows = (
                    session.cursor()
                    .execute(
                        "SELECT technical_name, cube_name FROM sap_bics_show(obj_type := ?, search := ?) "
                        "WHERE NOT is_folder ORDER BY 1",
                        [obj_type, pattern],
                    )
                    .fetchall()
                )
            except Exception as exc:
                raise traced(f"Could not list BW objects matching {pattern!r}", exc) from exc
            for technical_name, cube_name in rows:
                overrides.setdefault(
                    technical_name,
                    {"cube": cube_name or technical_name, "query": technical_name if obj_type == "QUERY" else None},
                )
        if not overrides:
            raise config_error(
                "No BW objects selected. Set 'query_pattern' (for example '*SALES*') and/or list "
                "cubes and BEx queries explicitly under 'objects'."
            )
        return overrides

    # ---- the stateful workflow ------------------------------------------------

    def check_incremental_config(self) -> None:
        """A BICS watermark re-reads its boundary period, so dedupe needs a key.

        The variable restricts the query to `>= last seen`, which necessarily
        includes the period the last run ended in. Without a declared primary key
        the destination cannot dedupe those rows and every run appends duplicates.
        """
        for name, override in self._object_overrides().items():
            if self.supports_incremental(override) and not override.get("primary_key"):
                raise config_error(
                    f"BW object {name!r} is configured for incremental sync but declares no "
                    "primary_key. The watermark re-reads the boundary period on every run, "
                    "so a key is needed for the destination to deduplicate it."
                )

    @staticmethod
    def supports_incremental(override: Mapping[str, Any]) -> bool:
        """BICS exposes no change tracking, so a watermark needs a BEx variable.

        A cursor field on its own would mean re-reading the whole query and
        discarding most of it, which is not incremental in any useful sense.
        """
        return bool(override.get("cursor_variable") and override.get("cursor_field"))

    def session_statements(
        self,
        obj: SapObject,
        extra_filter: tuple[str, Sequence[str]] | None = None,
        state: Mapping[str, Any] | None = None,
    ) -> list[str]:
        """The full begin -> configure -> result sequence for one BICS session."""
        override = self._object_overrides().get(obj.name, {})
        session_id = str(obj.meta["session_id"])
        cube = str(obj.meta["cube"])

        begin_args = [_lit(cube), f"id := {_lit(session_id)}", "return := 'RESULT'"]
        variables = list(override.get("variables") or [])

        # The watermark: restrict the query to everything at or after the highest
        # value seen last run, so BW does the filtering instead of the connector.
        cursor_variable = override.get("cursor_variable")
        cursor_field = override.get("cursor_field")
        if cursor_variable and cursor_field:
            watermark = (state or {}).get(str(cursor_field)) or override.get("cursor_start")
            if watermark not in (None, ""):
                # The same bound the RFC cursor has: this reaches BW as a
                # variable's LOW, and state is replayed by the platform.
                checked_state_value(str(cursor_field), watermark)
                variables.append({"name": cursor_variable, "sign": "I", "op": "GE", "low": str(watermark), "high": ""})

        if variables:
            rendered = []
            for var in variables:
                low = str(var.get("low", ""))
                high = str(var.get("high", ""))
                op = var.get("op") or ("BT" if high else "EQ")
                # `{'NAME': 'V', ...}`, not `{'V' AS NAME, ...}`: the latter is not
                # DuckDB struct syntax and fails to parse before it ever reaches
                # SAP. Every test here asserted substrings, so nothing noticed.
                rendered.append(
                    "{"
                    + ", ".join(
                        [
                            f"'NAME': {_lit(var.get('name', ''))}",
                            f"'SIGN': {_lit(var.get('sign', 'I'))}",
                            f"'OP': {_lit(op)}",
                            f"'LOW': {_lit(low)}",
                            f"'HIGH': {_lit(high)}",
                        ]
                    )
                    + "}"
                )
            begin_args.append("variables := [" + ", ".join(rendered) + "]")
        variant = override.get("variant")
        if variant:
            begin_args.append(f"variant := {_lit(variant)}")

        statements = [f"SELECT * FROM sap_bics_begin({', '.join(begin_args)})"]

        rows = override.get("rows") or []
        if rows:
            args = ", ".join(_lit(r) for r in rows)
            statements.append(f"SELECT * FROM sap_bics_rows({_lit(session_id)}, {args}, op := 'SET')")
        columns = override.get("columns") or []
        if columns:
            args = ", ".join(_lit(c) for c in columns)
            statements.append(f"SELECT * FROM sap_bics_columns({_lit(session_id)}, {args}, op := 'SET')")

        for member_filter in override.get("filters") or []:
            characteristic = member_filter.get("characteristic")
            members = member_filter.get("members") or []
            if not characteristic:
                continue
            rendered = "".join(f", {_lit(m)}" for m in members)
            statements.append(
                f"SELECT * FROM sap_bics_filter({_lit(session_id)}, {_lit(characteristic)}{rendered}, op := 'SET')"
            )

        if extra_filter is not None:
            characteristic, members = extra_filter
            rendered = "".join(f", {_lit(m)}" for m in members)
            statements.append(
                f"SELECT * FROM sap_bics_filter({_lit(session_id)}, {_lit(characteristic)}{rendered}, op := 'SET')"
            )

        for prop in override.get("properties") or []:
            statements.append(
                "SELECT * FROM sap_bics_set_char_prop("
                f"{_lit(session_id)}, {_lit(prop.get('characteristic', ''))}, "
                f"{_lit(prop.get('property', ''))}, {_lit(prop.get('value', ''))})"
            )

        statements.append(f"SELECT * FROM sap_bics_result({_lit(session_id)})")
        return statements

    # ---- reading --------------------------------------------------------------

    def read_plans(
        self, session: ErplSession, obj: SapObject, *, incremental: bool, state: Mapping[str, Any]
    ) -> list[ReadPlan]:
        override = self._object_overrides().get(obj.name, {})
        slice_by = override.get("slice_by") or {}
        characteristic = slice_by.get("characteristic")
        members = slice_by.get("members") or []

        if not (characteristic and members):
            statements = self.session_statements(obj, state=state)
            return [
                ReadPlan(
                    sql=statements[-1],
                    # The cube and query name the partition for anyone reading a
                    # log; the session id is a handle only this driver can use,
                    # so it travels in meta with the statements that set it up.
                    slice_={"cube": str(obj.meta["cube"]), "query": str(obj.meta.get("query") or obj.name)},
                    meta={"setup": statements[:-1], "session_id": obj.meta["session_id"]},
                )
            ]

        plans: list[ReadPlan] = []
        for member in members:
            sliced = SapObject(
                name=obj.name,
                json_schema=obj.json_schema,
                primary_key=obj.primary_key,
                supports_incremental=obj.supports_incremental,
                change_mode_field=obj.change_mode_field,
                meta={**obj.meta, "session_id": session_id_for(obj.name, str(member))},
            )
            statements = self.session_statements(sliced, extra_filter=(characteristic, [member]), state=state)
            plans.append(
                ReadPlan(
                    sql=statements[-1],
                    slice_={
                        "cube": str(obj.meta["cube"]),
                        "query": str(obj.meta.get("query") or obj.name),
                        "characteristic": characteristic,
                        "member": member,
                    },
                    meta={"setup": statements[:-1], "session_id": sliced.meta["session_id"]},
                )
            )
        return plans
