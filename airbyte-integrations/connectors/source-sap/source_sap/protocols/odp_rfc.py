"""SAP ODP over RFC (`erpl_odp`) -- full snapshots and server-side deltas.

The delta pointer lives on the SAP server, keyed by
``(context, odp_name, subscriber_name, subscriber_process)``.  ``subscriber_name``
is chosen by ERPL, so **the only thing this connector has to persist is the
``subscriber_process`` string** -- there is no client-side token.

The consequence is that losing Airbyte state orphans an ODQ subscription that
keeps retaining delta data on the SAP system, so the name is derived
deterministically from the stream rather than generated per run.
"""

from __future__ import annotations

import hashlib
import logging
import re
import threading
from collections.abc import Mapping
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
from source_sap.session import ErplSession
from source_sap.types import coerce_value, json_schema_for_fields, primary_key_for_fields

logger = logging.getLogger("airbyte")

# RODPS_REPL subscriber process is CHAR(32).
#: Sentinel distinguishing "no probe was taken this run" from "probed, unknown".
_NOT_PROBED = object()

_MAX_SUBSCRIBER_PROCESS = 32
_PREFIX = "AB_"

# Columns ODP adds to every record; they describe the change, not the entity.
ODP_CONTROL_FIELDS = ("ODQ_CHANGEMODE", "ODQ_ENTITYCNTR", "ODQ_TSN", "ODQ_UNITNO", "ODQ_RECORDNO")
CHANGE_MODE_FIELD = "ODQ_CHANGEMODE"


SUBSCRIBER_PROCESS_PATTERN = re.compile(r"^[A-Z0-9_]{1,32}$")


def subscriber_process_for(config: Mapping[str, Any], context: str, odp_name: str) -> str:
    """A stable, SAP-safe subscriber-process name for one stream.

    This is the ODQ subscription key on the SAP side, so it must be stable across
    runs -- a fresh name every sync would strand the previous subscription, which
    keeps retaining delta data -- and distinct between pipelines that read the
    same object, or they consume each other's deltas.

    The Airbyte protocol hands the connector no connection identifier, so the
    name is derived from the logon that distinguishes one source from another
    (system, client, user) plus the object. Two connections with *identical*
    config still collide; `warn_if_subscriber_derived` says so, and setting
    `subscriber_process` explicitly is the fix.
    """
    identity = "|".join(str(config.get(key) or "") for key in ("ashost", "mshost", "sysnr", "sysid", "client", "user"))
    digest = hashlib.sha1(f"{identity}|{context}|{odp_name}".encode()).hexdigest()[:10].upper()
    readable = re.sub(r"[^A-Za-z0-9]+", "_", odp_name).strip("_").upper()
    budget = _MAX_SUBSCRIBER_PROCESS - len(_PREFIX) - len(digest) - 1
    return f"{_PREFIX}{readable[:budget]}_{digest}"


def _lit(value: str) -> str:
    return sql_string_literal(str(value))


class OdpRfcDriver(ProtocolDriver):
    mode = "odp_rfc"
    required_extensions = ("erpl_rfc", "erpl_odp")

    def __init__(self, config: Mapping[str, Any]) -> None:
        super().__init__(config)
        # Streams whose delta read was skipped because SAP reported no change.
        # They opened no cursor, so there is nothing to close afterwards.
        self._skipped: set[str] = set()
        #: Last-modified value the skip decision was made on, per stream, so
        #: `next_state` records what the read started from rather than re-probing.
        self._probed: dict[str, str | None] = {}
        self._skipped_lock = threading.Lock()

    # ---- discovery ------------------------------------------------------------

    @retry_transient()
    def check(self, session: ErplSession) -> str:
        cursor = session.cursor()
        try:
            cursor.execute("PRAGMA sap_rfc_ping").fetchone()
            contexts = cursor.execute("SELECT technical_name FROM sap_odp_show_contexts()").fetchall()
        except Exception as exc:
            raise traced("SAP ODP connection test failed", exc) from exc
        names = ", ".join(row[0] for row in contexts) or "none"
        return f"Connected to SAP ODP. Available contexts: {names}."

    def discover(self, session: ErplSession) -> list[SapObject]:
        self.assert_no_subscriber_collisions()
        cursor = session.cursor()
        objects: list[SapObject] = []
        for context, odp_name, override in self._selected(session):
            try:
                row = cursor.execute(
                    "SELECT supports_full, supports_delta, fields "
                    f"FROM sap_odp_describe({_lit(context)}, {_lit(odp_name)})"
                ).fetchone()
            except Exception as exc:
                logger.warning("Skipping ODP %s/%s: %s", context, odp_name, exc)
                continue
            if not row:
                continue
            supports_delta, fields = bool(row[1]), list(row[2] or [])
            if not fields:
                logger.warning("Skipping ODP %s/%s: no fields reported.", context, odp_name)
                continue
            business = [f for f in fields if f.get("technical_name") not in ODP_CONTROL_FIELDS]
            subscriber = self._subscriber_for(context, odp_name, override)
            self.warn_if_subscriber_derived(odp_name)
            objects.append(
                SapObject(
                    name=f"{context}/{odp_name}",
                    json_schema=json_schema_for_fields(fields),
                    primary_key=(
                        [[k] for k in override["primary_key"]]
                        if override.get("primary_key")
                        else primary_key_for_fields(business)
                    ),
                    supports_incremental=supports_delta,
                    change_mode_field=CHANGE_MODE_FIELD if supports_delta else None,
                    meta={
                        "context": context,
                        "odp_name": odp_name,
                        "subscriber_process": subscriber,
                        "supports_delta": supports_delta,
                    },
                )
            )
        return objects

    def _subscriber_for(self, context: str, odp_name: str, override: Mapping[str, Any]) -> str:
        """The ODQ subscription key: explicit if configured, derived otherwise."""
        explicit = override.get("subscriber_process")
        if explicit is not None and str(explicit).strip() != "":
            candidate = str(explicit).strip()
            if not SUBSCRIBER_PROCESS_PATTERN.match(candidate):
                raise config_error(
                    f"subscriber_process {candidate!r} is not usable as a SAP ODQ subscriber "
                    "process. It must be 1-32 characters of A-Z, 0-9 and underscore."
                )
            return candidate
        return subscriber_process_for(self.config, context, odp_name)

    def assert_no_subscriber_collisions(self) -> None:
        """Two objects sharing one subscriber process share one ODQ subscription."""
        by_name: dict[str, list[str]] = {}
        for name, override in self._object_overrides().items():
            context = str(override.get("context") or self.options.get("context") or "")
            try:
                subscriber = self._subscriber_for(context, name, override)
            except Exception:
                continue  # invalid values are reported by _subscriber_for itself
            by_name.setdefault(subscriber, []).append(name)
        clashes = {sub: names for sub, names in by_name.items() if len(names) > 1}
        if clashes:
            detail = "; ".join(f"{sub} is used by {', '.join(sorted(names))}" for sub, names in sorted(clashes.items()))
            raise config_error(
                f"Several ODP objects resolve to the same subscriber_process ({detail}). "
                "They would share one SAP delta subscription and consume each other's "
                "changes. Give each object its own subscriber_process."
            )

    def warn_if_subscriber_derived(self, odp_name: str) -> None:
        """Say plainly that two identical connections would share a subscription."""
        override = self._object_overrides().get(odp_name, {})
        if str(override.get("subscriber_process") or "").strip():
            return
        logger.warning(
            "No subscriber_process is set for ODP object %s, so one is derived from the SAP "
            "logon and the object name. Two Airbyte connections with the same logon reading "
            "this object will share a single SAP delta subscription and consume each other's "
            "changes. Set subscriber_process explicitly on the object to keep them apart.",
            odp_name,
        )

    def _selected(self, session: ErplSession) -> list[tuple[str, str, Mapping[str, Any]]]:
        overrides = self._object_overrides()
        context = (self.options.get("context") or "").strip()
        pattern = (self.options.get("name_pattern") or "").strip()
        selected: list[tuple[str, str, Mapping[str, Any]]] = []
        seen: set[tuple[str, str]] = set()

        if pattern:
            if not context:
                raise config_error(
                    "An ODP context is required alongside 'name_pattern'. Pick one of the contexts "
                    "reported by the connection check, for example 'ABAP_CDS', 'BW' or 'SAPI'."
                )
            try:
                rows = (
                    session.cursor()
                    .execute(
                        f"SELECT technical_name FROM sap_odp_show({_lit(context)}, search := ?) ORDER BY 1",
                        [pattern],
                    )
                    .fetchall()
                )
            except Exception as exc:
                raise traced(f"Could not list ODP providers in context {context!r}", exc) from exc
            for row in rows:
                key = (context, row[0])
                if key not in seen:
                    seen.add(key)
                    selected.append((context, row[0], overrides.get(row[0], {})))

        for name, override in overrides.items():
            ctx = str(override.get("context") or context or "").strip()
            if not ctx:
                raise config_error(
                    f"ODP object {name!r} has no context. Set 'context' on the object or at the protocol level."
                )
            if (ctx, name) not in seen:
                seen.add((ctx, name))
                selected.append((ctx, name, override))

        if not selected:
            raise config_error(
                "No ODP providers selected. Set 'context' plus 'name_pattern', and/or list "
                "providers explicitly under 'objects'."
            )
        return selected

    def last_modified(self, session: ErplSession, context: str, odp_name: str) -> str | None:
        """The ODP object's last-changed timestamp, without fetching any rows.

        One RFC call and no extraction, so it is worth spending before opening a
        delta cursor on a stream that is usually quiet. Returns None when SAP
        cannot say -- the probe is an optimisation and must never fail a sync.
        """
        try:
            row = (
                session.cursor()
                .execute(f"SELECT * FROM sap_odp_get_last_modified({_lit(context)}, {_lit(odp_name)})")
                .fetchone()
            )
        except Exception as exc:
            logger.debug("Last-modified probe for %s/%s failed: %s", context, odp_name, exc)
            return None
        if not row or row[1] is None:
            return None
        return str(coerce_value(row[1]))

    def _remember_probe(self, stream: str, value: str | None) -> None:
        with self._skipped_lock:
            self._probed[stream] = value

    def _is_unchanged(self, session: ErplSession, obj: SapObject, state: Mapping[str, Any]) -> bool:
        """True when SAP reports the object has not changed since the last run.

        The probed value is remembered for `next_state`, which must record the
        timestamp the read *started* from. Probing again afterwards would stamp
        changes that landed during the sync as already consumed, and the next run
        would skip them.
        """
        # The probe always runs, before the read: `skip_unchanged` governs only
        # whether its result may skip the extraction. Taking the reading after
        # the read would stamp changes that landed during the sync as consumed.
        current = self.last_modified(session, str(obj.meta["context"]), str(obj.meta["odp_name"]))
        self._remember_probe(obj.name, current)
        if self.options.get("skip_unchanged") is False:
            return False

        previous = state.get("last_modified")
        if not (previous and state.get("initialized")):
            return False  # nothing to compare against, or no DELTAINIT yet
        if current is None:
            return False
        return current == str(previous)

    # ---- reading --------------------------------------------------------------

    def read_plans(
        self, session: ErplSession, obj: SapObject, *, incremental: bool, state: Mapping[str, Any]
    ) -> list[ReadPlan]:
        context = str(obj.meta["context"])
        odp_name = str(obj.meta["odp_name"])
        override = self._object_overrides().get(odp_name, {})

        if incremental:
            if self._is_unchanged(session, obj, state):
                logger.info(
                    "%s is unchanged on SAP since the last sync; skipping the delta read.",
                    obj.name,
                )
                with self._skipped_lock:
                    self._skipped.add(obj.name)
                return []
            subscriber = str(state.get("subscriber_process") or obj.meta["subscriber_process"])
            args = [_lit(context), _lit(odp_name), _lit(subscriber)]
            # Deliberately no THREADS: erpl caps delta fetch to one worker because
            # a parallel multi-package delta can silently under-count.
            self._append_projection(args, override)
            sql = f"SELECT * FROM sap_odp_read_delta({', '.join(args)})"
            return [ReadPlan(sql=sql, slice_={"odp": odp_name, "mode": "delta"})]

        args = [_lit(context), _lit(odp_name)]
        threads = clamp(override.get("threads", self.options.get("threads")), 1, 32)
        if threads is not None:
            args.append(f"THREADS := {threads}")
        self._append_projection(args, override)
        sql = f"SELECT * FROM sap_odp_read_full({', '.join(args)})"
        return [ReadPlan(sql=sql, slice_={"odp": odp_name, "mode": "full"})]

    @staticmethod
    def _append_projection(args: list[str], override: Mapping[str, Any]) -> None:
        columns = override.get("columns")
        if columns:
            args.append("COLUMNS := [" + ", ".join(_lit(c) for c in columns) + "]")
        filters = override.get("filters")
        if filters:
            rendered = []
            for f in filters:
                pairs = ", ".join(
                    f"{_lit(str(v))} AS {key}"
                    for key, v in (
                        ("FIELDNAME", f.get("fieldname")),
                        ("SIGN", f.get("sign", "I")),
                        ("OP", f.get("op", "EQ")),
                        ("LOW", f.get("low", "")),
                        ("HIGH", f.get("high", "")),
                    )
                )
                rendered.append(f"{{{pairs}}}")
            args.append("FILTERS := [" + ", ".join(rendered) + "]")

    # ---- state ----------------------------------------------------------------

    def next_state(self, session: ErplSession, obj: SapObject, previous: Mapping[str, Any]) -> Mapping[str, Any]:
        state = dict(previous)
        state["subscriber_process"] = str(previous.get("subscriber_process") or obj.meta["subscriber_process"])
        state["context"] = obj.meta["context"]
        state["odp_name"] = obj.meta["odp_name"]
        state["initialized"] = True
        with self._skipped_lock:
            probed = self._probed.get(obj.name, _NOT_PROBED)
        if probed is _NOT_PROBED:
            # Full refresh never probes; take a reading now, before any later
            # change can be mistaken for one this run consumed.
            probed = self.last_modified(session, str(obj.meta["context"]), str(obj.meta["odp_name"]))
        if probed is not None:
            state["last_modified"] = probed
        return state

    def release(self, session: ErplSession, obj: SapObject, state: Mapping[str, Any]) -> None:
        """Release the server-side delta cursor; the subscription itself survives.

        Runs after a failed read too. Closing is not confirming -- erpl calls
        RODPS_REPL_ODP_CLOSE, and a cursor left mid-fetch is refused rather than
        silently consumed -- so this cannot cost the next run its packets, and a
        refusal is reported instead of a cursor nobody knew was open.
        """
        with self._skipped_lock:
            # Read membership then clear it: a second read of the same stream in
            # one process must not inherit a stale skip and leave a real cursor
            # open on the SAP side.
            was_skipped = obj.name in self._skipped
            self._skipped.discard(obj.name)
        if was_skipped:
            return  # nothing was opened, so there is nothing to close
        # `on_success` runs before `next_state`, so on the first incremental run
        # the state blob is still empty -- fall back to the derived name the read
        # actually used, or the DELTAINIT leaves a cursor reserved on SAP.
        subscriber = state.get("subscriber_process") or obj.meta.get("subscriber_process")
        if not subscriber:
            return
        context, odp_name = str(obj.meta["context"]), str(obj.meta["odp_name"])
        try:
            result = (
                session.cursor()
                .execute(f"PRAGMA sap_odp_close_delta_cursor({_lit(context)}, {_lit(subscriber)}, {_lit(odp_name)})")
                .fetchone()
            )
        except Exception as exc:
            logger.warning("Could not close the ODP delta cursor for %s: %s", obj.name, exc)
            return
        status = result[0] if result else "UNKNOWN"
        if status == "CLOSED":
            logger.info("Closed the ODP delta cursor for %s.", obj.name)
        elif status == "NOT_FOUND":
            logger.debug("No open ODP delta cursor for %s.", obj.name)
        else:
            # REFUSED / STILL_OPEN leave a cursor reserved on the SAP side.
            logger.warning(
                "The ODP delta cursor for %s could not be closed (%s). It stays reserved on SAP; "
                "the next sync recovers it, or clear it with PRAGMA sap_odp_drop.",
                obj.name,
                status,
            )
