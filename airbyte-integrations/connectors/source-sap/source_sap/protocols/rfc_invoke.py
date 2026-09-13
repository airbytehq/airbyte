"""Calling SAP RFC function modules as Airbyte streams (`erpl_rfc`).

Two constraints shape this driver.

**`discover` never invokes anything.** Learning a stream's shape by calling the
function module would mean a source connector calling, say, `BAPI_*_CREATE` just
to see what comes back. It isn't acceptable, and it isn't necessary:
`sap_rfc_describe_function` reports each parameter's DuckDB type as a string, and
DuckDB will parse that string into columns for us. So there is also no pattern
discovery here -- only function modules listed explicitly in the config are ever
called.

**BAPIs fail by returning, not by raising.** The classic BAPI contract puts
errors in a `RETURN` table with `TYPE = 'E'` or `'A'` and answers `RFC_OK`. A
connector that reads only the payload table turns such a failure into an empty
stream. So the call is made *without* `path`, which yields one row holding every
result parameter, and `RETURN` is inspected before a single record is emitted.
"""

from __future__ import annotations

import logging
import re
from collections.abc import Iterator, Mapping, Sequence
from typing import Any

import duckdb

from source_sap.duck import columns_of, schema_from_description
from source_sap.errors import config_error, traced
from source_sap.protocols.base import (
    ProtocolDriver,
    ReadPlan,
    SapObject,
    sql_string_literal,
    sql_struct_literal,
)
from source_sap.retry import retry_transient
from source_sap.sap_values import checked_state_value, sap_date, sap_time, sap_timestamp
from source_sap.session import ErplSession
from source_sap.types import coerce_value

logger = logging.getLogger("airbyte")

#: BAPI RETURN message types that mean the call failed.
FAILURE_TYPES = frozenset({"E", "A"})

_INTEGER_TYPES = frozenset(
    {"TINYINT", "SMALLINT", "INTEGER", "BIGINT", "HUGEINT", "UTINYINT", "USMALLINT", "UINTEGER", "UBIGINT"}
)

#: Result parameter blocks of a function module, in the order a `path` is resolved.
RESULT_BLOCKS = ("tables", "export", "changing")
PARAMETER_BLOCKS = ("import", "export", "changing", "tables")


#: Names SAP modules use for the BAPI return table. `RETURN` is the classic one,
#: but modules are free to prefix by direction and plenty do.
RETURN_NAMES = ("RETURN", "E_RETURN", "ET_RETURN", "EX_RETURN", "T_RETURN", "RETURN_TAB")

#: Fields that mark a row type as BAPIRET-shaped, used to warn about a module
#: whose return table is named something else entirely.
RETURN_SHAPE_FIELDS = frozenset({"TYPE", "MESSAGE", "ID", "NUMBER"})


def _message_field(message: Mapping[str, Any], field: str) -> Any:
    """Read a BAPIRET field however the source spelled its key."""
    if field in message:
        return message[field]
    wanted = field.upper()
    for key, value in message.items():
        if str(key).upper() == wanted:
            return value
    return None


def _as_messages(return_table: Any) -> list[Mapping[str, Any]]:
    """Normalise a RETURN parameter to a list of messages.

    It usually arrives as a table, but a module declaring it as a single
    structure yields a Mapping -- and iterating that yields its *keys*, so
    `.get` on each would raise and a healthy call would fail as hard as a
    broken one.
    """
    if return_table is None:
        return []
    if isinstance(return_table, Mapping):
        return [return_table]
    if isinstance(return_table, (list, tuple)):
        return [m for m in return_table if isinstance(m, Mapping)]
    return []


def find_return_field(columns: Sequence[str], configured: str | None = None) -> str | None:
    """Which result column holds the BAPI return table.

    Matched case-insensitively: SAP spells its parameters in upper case, but the
    cost of being wrong here is that a failed call reads as an empty stream, so
    the match is deliberately generous.
    """
    by_upper = {str(c).upper(): c for c in columns}
    if configured:
        return by_upper.get(str(configured).upper())
    for name in RETURN_NAMES:
        if name in by_upper:
            return by_upper[name]
    return None


#: A DDIC-derived type string: identifiers, the punctuation DuckDB needs for
#: STRUCT and DECIMAL, and nothing that could start a second statement.
_SAFE_TYPE = re.compile(r'^[A-Za-z0-9_,() \[\]"]+$')


def is_sap_type_safe(duckdb_type: str) -> bool:
    """Whether a type string SAP reported is safe to interpolate into SQL.

    Config values are funnelled through `sql_string_literal`, but these come
    from `sap_rfc_describe_function` and are spliced in as SQL *syntax*, which
    no amount of quoting would cover. It is a trust-boundary question rather
    than a user-input hole -- it needs a hostile or compromised SAP, or a MITM
    on the unencrypted RFC transport -- and it is cheap to close.
    """
    text = str(duckdb_type).strip()
    if not text or not _SAFE_TYPE.match(text):
        return False
    return "--" not in text and "/*" not in text


def _struct_field_names(duckdb_type: str) -> list[str]:
    """Field names of a STRUCT type string, good enough to recognise BAPIRET."""
    if not duckdb_type.upper().startswith("STRUCT("):
        return []
    inner = duckdb_type[duckdb_type.index("(") + 1 : duckdb_type.rindex(")")]
    return [m.group(1).strip('"').upper() for m in re.finditer(r'(?:^|,)\s*("?[\w]+"?)\s', inner)]


def is_bapi_failure(return_table: Any) -> bool:
    """True when a BAPI return table carries an error or abort message."""
    for message in _as_messages(return_table):
        kind = str(_message_field(message, "TYPE") or "").strip().upper()
        if kind in FAILURE_TYPES:
            return True
    return False


def describe_failure(return_table: Any) -> str:
    """The SAP messages from a failed call, as one line."""
    parts = []
    for message in _as_messages(return_table):
        # Through `_message_field`, like `is_bapi_failure`: the two must agree
        # about what a message says, or a classified failure describes itself as
        # nothing at all.
        if str(_message_field(message, "TYPE") or "").strip().upper() not in FAILURE_TYPES:
            continue
        text = str(_message_field(message, "MESSAGE") or "").strip()
        ident = "/".join(
            str(_message_field(message, key) or "") for key in ("ID", "NUMBER") if _message_field(message, key)
        )
        parts.append(f"{text} ({ident})" if ident else text)
    return "; ".join(p for p in parts if p)


class RfcInvokeDriver(ProtocolDriver):
    mode = "rfc_invoke"
    required_extensions = ("erpl_rfc",)

    # ---- lifecycle ------------------------------------------------------------

    @retry_transient()
    def check(self, session: ErplSession) -> str:
        """Ping only. Calling the configured function modules would be a side effect."""
        cursor = session.cursor()
        try:
            cursor.execute("PRAGMA sap_rfc_ping").fetchone()
        except Exception as exc:
            raise traced("SAP RFC connection test failed", exc) from exc
        names = [str(o.get("function")) for o in self._objects() if o.get("function")]
        for name in names:
            self._describe(cursor, name)  # metadata only, no invocation
        return f"Connected to SAP via RFC. Function modules resolved: {', '.join(names)}."

    def discover(self, session: ErplSession) -> list[SapObject]:
        cursor = session.cursor()
        objects: list[SapObject] = []
        for entry in self._objects():
            function = str(entry.get("function") or "").strip()
            if not function:
                raise config_error(
                    f"The RFC object {entry.get('name') or '<unnamed>'!r} has no 'function'. "
                    "Name the RFC function module to call."
                )
            described = self._describe(cursor, function)
            parameters = dict(entry.get("parameters") or {})
            slice_by = entry.get("slice_by") or {}
            cursor_parameter = entry.get("cursor_parameter")
            # F7: every name that ends up in the call must be validated, not just
            # the static ones -- a typo in either would otherwise surface
            # mid-sync as an opaque SAP dump after discovery said all was well.
            self.validate_parameters(
                function,
                {
                    **parameters,
                    **({str(slice_by["parameter"]): None} if slice_by.get("parameter") else {}),
                    **({str(cursor_parameter): None} if cursor_parameter else {}),
                },
                described,
            )
            parameters = self.canonical_parameters(parameters, described)

            path = str(entry.get("path") or "").strip()
            if path:
                path_field, duckdb_type = self.resolve_path(function, path, described)
            else:
                path_field, duckdb_type = None, self._scalar_export_type(described)

            schema = self.schema_for_duckdb_type(cursor, duckdb_type)
            cursor_field = entry.get("cursor_field")
            objects.append(
                SapObject(
                    name=str(entry.get("name") or function),
                    json_schema=schema,
                    primary_key=[[k] for k in (entry.get("primary_key") or [])] or None,
                    supports_incremental=bool(cursor_field and cursor_parameter),
                    meta={
                        "function": function,
                        "path": path,
                        "path_field": path_field,
                        "parameters": parameters,
                        "cursor_field": cursor_field,
                        "cursor_parameter": cursor_parameter,
                        "slice_by": slice_by,
                        "return_field": self._return_field(function, described, entry),
                        "export_fields": None if path else list(schema["properties"]),
                        "parameter_types": {
                            str(p["name"]): str(p.get("duckdb_type") or "")
                            for block in PARAMETER_BLOCKS
                            for p in described.get(block, [])
                            if p.get("name")
                        },
                    },
                )
            )
        return objects

    def _objects(self) -> list[Mapping[str, Any]]:
        objects = list(self.options.get("objects") or [])
        if not objects:
            raise config_error(
                "No RFC function modules configured. List them under 'objects'. There is "
                "deliberately no pattern discovery for this protocol: finding function "
                "modules by pattern would mean calling them to see what they do."
            )
        return objects

    # ---- metadata -------------------------------------------------------------

    def _describe(self, cursor: duckdb.DuckDBPyConnection, function: str) -> dict[str, list[Mapping[str, Any]]]:
        try:
            row = cursor.execute(
                "SELECT import, export, changing, tables "
                f"FROM sap_rfc_describe_function({sql_string_literal(function)})"
            ).fetchone()
        except Exception as exc:
            raise traced(f"Could not read the interface of {function}", exc) from exc
        if not row:
            raise config_error(
                f"SAP reports no RFC function module named {function!r}. Check the name and "
                "that the module is flagged remote-enabled."
            )
        return {block: list(row[i] or []) for i, block in enumerate(PARAMETER_BLOCKS)}

    def _return_field(self, function: str, described: Mapping[str, Any], entry: Mapping[str, Any]) -> str | None:
        """Which result parameter to inspect for BAPI error messages.

        Fails at discover when a module clearly has a return table under an
        unrecognised name: a missed return table means a failed call is reported
        as an empty stream, which is the one outcome this driver exists to avoid.
        """
        names = [str(p["name"]) for block in RESULT_BLOCKS for p in described.get(block, []) if p.get("name")]
        configured = entry.get("return_parameter")
        if configured:
            if str(configured) not in names:
                raise config_error(
                    f"{function} has no result parameter {configured!r}. Available: "
                    f"{', '.join(sorted(names)) or 'none'}."
                )
            return str(configured)

        found = find_return_field(names)
        if found:
            return found

        # No conventional name -- is there something return-shaped anyway?
        for block in RESULT_BLOCKS:
            for parameter in described.get(block, []):
                declared = str(parameter.get("duckdb_type") or "").upper()
                if len(RETURN_SHAPE_FIELDS & set(_struct_field_names(declared))) >= 3:
                    raise config_error(
                        f"{function} reports errors in {parameter['name']!r}, which this "
                        "connector does not recognise as a return table. Set "
                        "'return_parameter' on the object so BAPI errors are not silently "
                        "read as an empty result."
                    )
        return None

    def canonical_parameters(self, parameters: Mapping[str, Any], described: Mapping[str, Any]) -> dict[str, Any]:
        """Re-spell parameter names the way SAP spells them.

        Validation is case-insensitive, so `{"flightdate": ...}` passes; the type
        lookup that follows is keyed on SAP's spelling, so it would then miss the
        DATE cast and the call would fail at SAP with exactly the error the
        casting layer exists to prevent.
        """
        by_upper = {
            str(p["name"]).upper(): str(p["name"])
            for block in PARAMETER_BLOCKS
            for p in described.get(block, [])
            if p.get("name")
        }
        return {by_upper.get(str(k).upper(), str(k)): v for k, v in parameters.items()}

    def validate_parameters(self, function: str, parameters: Mapping[str, Any], described: Mapping[str, Any]) -> None:
        """Reject unknown parameter names before SAP turns them into a dump."""
        known = {
            str(p.get("name")).upper() for block in PARAMETER_BLOCKS for p in described.get(block, []) if p.get("name")
        }
        unknown = [name for name in parameters if str(name).upper() not in known]
        if unknown:
            raise config_error(
                f"{function} has no parameter(s) {', '.join(sorted(unknown))}. "
                f"Available parameters: {', '.join(sorted(known))}."
            )

    def resolve_path(self, function: str, path: str, described: Mapping[str, Any]) -> tuple[str, str]:
        """Map a `path` onto the result parameter it selects, and its DuckDB type."""
        wanted = path.strip().lstrip("/").upper()
        for block in RESULT_BLOCKS:
            for parameter in described.get(block, []):
                if str(parameter.get("name") or "").upper() == wanted:
                    return str(parameter["name"]), str(parameter["duckdb_type"])
        available = sorted(
            str(p.get("name")) for block in RESULT_BLOCKS for p in described.get(block, []) if p.get("name")
        )
        raise config_error(
            f"{function} has no result parameter {path!r}. Available result parameters: "
            f"{', '.join(available) or 'none'}."
        )

    @staticmethod
    def _scalar_export_type(described: Mapping[str, Any]) -> str:
        """With no `path`, the stream is the function's scalar export parameters."""
        fields = [
            f"{p['name']} {p['duckdb_type']}"
            for block in ("export", "changing")
            for p in described.get(block, [])
            if p.get("name")
            and not str(p.get("duckdb_type", "")).endswith("[]")
            and is_sap_type_safe(str(p.get("duckdb_type", "")))
            and is_sap_type_safe(str(p["name"]))
        ]
        if not fields:
            raise config_error(
                "This function module has no scalar export parameters, so there is nothing "
                "to emit without a 'path'. Set 'path' to one of its result tables."
            )
        return "STRUCT(" + ", ".join(fields) + ")"

    @staticmethod
    def render_parameters(parameters: Mapping[str, Any], parameter_types: Mapping[str, str]) -> str:
        """Render the parameter struct, casting each value to its declared type.

        A connector config is JSON, so a date arrives as a string and SAP refuses
        it outright: *"Parameter 'FLIGHTDATE' is of type 'RFCTYPE_DATE' (RFC) but
        argument is of type 'VARCHAR' (DuckDB)"*. The type that
        `sap_rfc_describe_function` reported is what tells us how to cast.

        Only top-level parameters are cast; members of a SAP structure are left
        as written, which is what ERPL's structure mapping expects.
        """
        rendered = []
        for name, value in parameters.items():
            declared = str(parameter_types.get(str(name), "")).strip().upper()
            rendered.append(f"{sql_string_literal(name)}: {RfcInvokeDriver._render_value(name, value, declared)}")
        return "{" + ", ".join(rendered) + "}"

    @staticmethod
    def _render_value(name: str, value: Any, declared: str) -> str:
        if value is None or isinstance(value, (Mapping, list, tuple, bool)):
            return sql_struct_literal(value)
        try:
            if declared and not is_sap_type_safe(declared):
                declared = ""  # fall through to a plain literal
            if declared == "DATE":
                return f"DATE {sql_string_literal(sap_date(str(value)))}"
            if declared == "TIME":
                return f"TIME {sql_string_literal(sap_time(str(value)))}"
            if declared.startswith("TIMESTAMP"):
                return f"TIMESTAMP {sql_string_literal(sap_timestamp(str(value)))}"
            if declared.startswith("DECIMAL"):
                return f"{sql_string_literal(str(value))}::{declared}"
            if declared in _INTEGER_TYPES:
                return f"{int(value)}::{declared}"
            if declared in ("FLOAT", "DOUBLE", "REAL"):
                return f"{float(value)}::{declared}"
        except (ValueError, TypeError) as exc:
            raise config_error(
                f"The value for RFC parameter {name!r} does not fit its SAP type {declared}: {exc}"
            ) from exc
        return sql_struct_literal(value)

    @staticmethod
    def schema_for_duckdb_type(cursor: duckdb.DuckDBPyConnection, duckdb_type: str) -> dict[str, Any]:
        """Expand a DuckDB STRUCT type string into a JSON Schema.

        This is what lets `discover` work off metadata: DuckDB parses the type
        string that `sap_rfc_describe_function` reported, and the resulting
        column descriptions go through the same path as every other protocol.
        """
        if not is_sap_type_safe(duckdb_type):
            raise config_error(
                f"SAP reported an unexpected parameter type {duckdb_type!r}. The connector "
                "will not interpolate it into a query."
            )
        element = duckdb_type.strip()
        if element.endswith("[]"):
            element = element[:-2]
        try:
            result = cursor.execute(f"SELECT s.* FROM (SELECT NULL::{element} AS s) WHERE false")
            schema = schema_from_description(result.description)
        except Exception as exc:
            raise config_error(
                f"Could not interpret the SAP parameter type {duckdb_type!r} reported by the function module: {exc}"
            ) from exc
        if not schema["properties"]:
            raise config_error(f"The SAP parameter type {duckdb_type!r} has no fields, so it cannot become a stream.")
        return schema

    # ---- reading --------------------------------------------------------------

    def read_plans(
        self, session: ErplSession, obj: SapObject, *, incremental: bool, state: Mapping[str, Any]
    ) -> list[ReadPlan]:
        function = str(obj.meta["function"])
        base_parameters = dict(obj.meta.get("parameters") or {})

        if incremental:
            cursor_field = obj.meta.get("cursor_field")
            cursor_parameter = obj.meta.get("cursor_parameter")
            since = state.get(str(cursor_field)) if cursor_field else None
            if cursor_parameter and since not in (None, ""):
                # Bounded like the other two state sinks: a CHAR-typed parameter
                # is not saved by the strict `sap_date` the typed ones get.
                checked_state_value(str(cursor_field), since)
                base_parameters[str(cursor_parameter)] = since

        slice_by = obj.meta.get("slice_by") or {}
        parameter, values = slice_by.get("parameter"), list(slice_by.get("values") or [])
        if not (parameter and values):
            return [self._plan(function, base_parameters, obj, {})]
        return [
            self._plan(function, {**base_parameters, str(parameter): value}, obj, {str(parameter): value})
            for value in values
        ]

    def _plan(
        self,
        function: str,
        parameters: Mapping[str, Any],
        obj: SapObject,
        slice_keys: Mapping[str, Any],
    ) -> ReadPlan:
        args = [sql_string_literal(function)]
        if parameters:
            args.append(self.render_parameters(dict(parameters), obj.meta.get("parameter_types") or {}))
        # Deliberately no `path`: the call has to return every result parameter so
        # that RETURN can be checked alongside the payload, from one invocation.
        return ReadPlan(
            sql=f"SELECT * FROM sap_rfc_invoke({', '.join(args)})",
            # The function module names the partition even when nothing slices
            # it: an unsliced plan with an empty identity logs as a partition
            # nobody can tell from any other.
            slice_={"function": function, **dict(slice_keys)},
            meta={
                "function": function,
                "path_field": obj.meta.get("path_field"),
                "return_field": obj.meta.get("return_field"),
                "export_fields": obj.meta.get("export_fields"),
            },
        )

    def records_from(self, plan: ReadPlan, cursor: duckdb.DuckDBPyConnection) -> Iterator[dict[str, Any]]:
        result = plan.execute(cursor)
        columns = columns_of(result.description)
        row = result.fetchone()
        if row is None:
            return
        values = dict(zip(columns, row, strict=False))

        return_field = plan.meta.get("return_field") or find_return_field(columns)
        return_table = values.get(return_field) if return_field else None
        if is_bapi_failure(return_table):
            function = plan.meta.get("function", "the function module")
            raise config_error(f"{function} reported an error: {describe_failure(return_table)}")

        path_field = plan.meta.get("path_field")
        if not path_field:
            # No path: the scalar export parameters are the single record.
            # Projected against what discovery promised, so the records and the
            # schema cannot disagree about which fields exist.
            declared = plan.meta.get("export_fields")
            yield {
                key: coerce_value(value)
                for key, value in values.items()
                if not isinstance(value, list) and (declared is None or key in declared)
            }
            return

        for entry in values.get(path_field) or []:
            yield {key: coerce_value(value) for key, value in (entry or {}).items()}
