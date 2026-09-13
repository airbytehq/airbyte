"""SAP ODP over the Gateway OData protocol (`erpl_web`).

Unlike the RFC flavour, the delta position here *is* a client-side token.
erpl_web keeps it in its own ``erpl_web.odp_subscriptions`` table inside a
persistent DuckDB file -- but for Airbyte the connector state is the source of
truth, and the DuckDB file is scratch.

So each sync seeds erpl_web's table from Airbyte state before reading, and reads
the advanced token back out afterwards.  (The documented ``import_delta_token``
parameter is the intended route, but it times out against a slow Gateway; the
seed is what actually works.)
"""

from __future__ import annotations

import logging
from collections.abc import Mapping, Sequence
from typing import Any
from urllib.parse import urlsplit

from source_sap.duck import schema_from_description
from source_sap.errors import config_error, traced
from source_sap.protocols.base import ProtocolDriver, ReadPlan, SapObject, clamp
from source_sap.session import ErplSession
from source_sap.types import coerce_value

logger = logging.getLogger("airbyte")

CHANGE_MODE_CANDIDATES = ("ODQ_CHANGEMODE", "RECORD_MODE")
ENTITY_COUNTER_CANDIDATES = ("ODQ_ENTITYCNTR",)


class OdpODataDriver(ProtocolDriver):
    mode = "odp_odata"
    required_extensions = ("erpl_web",)

    # ---- discovery ------------------------------------------------------------

    def check(self, session: ErplSession) -> str:
        """Probe a configured entity set if there is one, else the Gateway root.

        Probing the entity set is what actually exercises the credentials and the
        user's authorization for the service; the Gateway root answers 404 on a
        stock system, which proves only that something is listening.
        """
        base_url = self._base_url()
        targets = [self._resolve_url(str(o.get("url") or k)) for k, o in self._object_overrides().items()]
        probe = targets[0] if targets else base_url.rstrip("/") + "/sap/opu/odata/"
        try:
            # Auth comes from the URL-scoped http_basic secret, the same path the
            # reads use. Passing the credential inline would put it one DuckDB
            # error message away from the logs.
            row = session.cursor().execute("SELECT status FROM http_get(?)", [probe]).fetchone()
        except Exception as exc:
            raise traced(f"Could not reach the SAP Gateway at {base_url}", exc) from exc

        status = int(row[0]) if row else 0
        if status in (401, 403):
            raise config_error(
                f"The SAP Gateway rejected the credentials for {probe} (HTTP {status}). "
                "Check the user and password, and that the user is authorised for this service."
            )
        if status == 404 and targets:
            raise config_error(
                f"The SAP Gateway has no service at {probe} (HTTP 404). Check the entity-set "
                "URL, and that the OData service is activated in transaction /IWFND/MAINT_SERVICE."
            )
        if status >= 500:
            raise config_error(f"The SAP Gateway at {base_url} returned HTTP {status} for {probe}.")
        return f"Reached the SAP Gateway at {base_url} (HTTP {status} for {probe})."

    def warn_about_insecure_transport(self) -> None:
        if (self.config.get("base_url") or "").strip().lower().startswith("http://"):  # ignore-https-check
            logger.warning(
                "The SAP Gateway base URL uses plain http, so the password and all extracted "
                "data travel in the clear. Use https for anything other than a local test system."
            )

    def _base_url(self) -> str:
        base_url = (self.config.get("base_url") or "").strip()
        if not base_url:
            raise config_error(
                "ODP over OData needs the SAP Gateway base URL, for example 'https://sap.example.com:44300'."
            )
        return base_url

    def discover(self, session: ErplSession) -> list[SapObject]:
        entries = self._selected_entity_sets(session)
        objects: list[SapObject] = []
        for url, override in entries:
            entity_set = str(override.get("entity_set") or url.rstrip("/").rsplit("/", 1)[-1])
            schema, change_field = self._describe(session, url)
            if schema is None:
                continue
            objects.append(
                SapObject(
                    name=entity_set,
                    json_schema=schema,
                    primary_key=[[k] for k in (override.get("primary_key") or [])] or None,
                    supports_incremental=True,
                    change_mode_field=change_field,
                    meta={"entity_set_url": url, "entity_set": entity_set},
                )
            )
        return objects

    def _describe(self, session: ErplSession, url: str) -> tuple[dict[str, Any] | None, str | None]:
        """Infer a schema from a zero-row read; keeps discovery cheap and honest."""
        try:
            cursor = session.cursor()
            cursor.execute("SELECT * FROM odp_odata_read(?) LIMIT 0", [url])
            schema = schema_from_description(cursor.description)
        except Exception as exc:
            logger.warning("Skipping ODP OData entity set %s: %s", url, exc)
            return None, None
        properties = schema["properties"]
        if not properties:
            logger.warning("Skipping ODP OData entity set %s: it exposes no columns.", url)
            return None, None
        change_field = next((c for c in CHANGE_MODE_CANDIDATES if c in properties), None)
        if change_field is None:
            # Incremental still works -- new and changed rows arrive -- but a
            # deleted row simply stops appearing, so the destination keeps it.
            # Said once at discovery, where the choice of entity set is made.
            logger.warning(
                "%s exposes no change-mode column (%s), so this stream cannot report "
                "deletes: an incremental sync will add and update rows but never mark "
                "one deleted. Enable change tracking on the ODP service to get "
                "tombstones.",
                url,
                "/".join(CHANGE_MODE_CANDIDATES),
            )
        return schema, change_field

    def _resolve_url(self, url: str) -> str:
        """Resolve an entity-set URL and confine it to the configured Gateway.

        An absolute URL in the config would otherwise let the connector fetch any
        host reachable from its network position, using credentials scoped to the
        Gateway.
        """
        base_url = self._base_url()
        text = str(url).strip()
        if not text.lower().startswith(("http://", "https://")):  # ignore-https-check
            return base_url.rstrip("/") + "/" + text.lstrip("/")
        base, target = urlsplit(base_url), urlsplit(text)
        if (target.scheme, target.netloc) != (base.scheme, base.netloc):
            raise config_error(
                f"The entity-set URL {text!r} points at {target.scheme}://{target.netloc}, "
                f"which is not the configured base_url ({base.scheme}://{base.netloc}). "
                "Use a path relative to base_url, or change base_url."
            )
        return text

    def _selected_entity_sets(self, session: ErplSession) -> list[tuple[str, Mapping[str, Any]]]:
        overrides = self._object_overrides()
        entries: list[tuple[str, Mapping[str, Any]]] = []
        seen: set[str] = set()

        for key, override in overrides.items():
            url = self._resolve_url(str(override.get("url") or key))
            if url not in seen:
                seen.add(url)
                entries.append((url, override))

        service_pattern = (self.options.get("service_pattern") or "").strip()
        if service_pattern:
            for url, meta in self._catalog_entity_sets(session, service_pattern):
                if url not in seen:
                    seen.add(url)
                    entries.append((url, meta))

        if not entries:
            raise config_error(
                "No ODP OData entity sets selected. List them under 'objects' as full entity-set "
                "URLs (for example '/sap/opu/odata/sap/Z_ODP_SRV/FactsOfZ'), and/or set "
                "'service_pattern' to discover them from the Gateway catalog service."
            )
        return entries

    def _catalog_entity_sets(self, session: ErplSession, pattern: str) -> list[tuple[str, Mapping[str, Any]]]:
        """Best-effort catalog discovery.

        `odp_odata_show` fails against some Gateway releases with an INTERNAL
        error that invalidates the whole DuckDB instance, so it runs on a
        throwaway connection and a failure degrades to "configure URLs explicitly".
        """
        connection = None
        try:
            connection = session.disposable()
            rows = connection.execute(
                "SELECT entity_set_url, entity_set_id, change_tracking FROM odp_odata_show(?) WHERE service_id ILIKE ?",
                [self._base_url(), pattern.replace("*", "%")],
            ).fetchall()
        except Exception as exc:
            logger.warning(
                "ODP OData catalog discovery failed (%s). List entity-set URLs under 'objects' instead.",
                str(exc).splitlines()[0] if str(exc) else exc,
            )
            return []
        finally:
            if connection is not None:
                connection.close()
        # Through the same confinement configured URLs go through: the catalog
        # is the Gateway's answer, and a compromised or impersonated Gateway
        # must not be able to name a host the connector then fetches.
        confined: list[tuple[str, Mapping[str, Any]]] = []
        for row in rows:
            try:
                confined.append((self._resolve_url(str(row[0])), {"entity_set": row[1]}))
            except Exception as exc:
                logger.warning("Skipping catalog entity set %s: %s", row[1], exc)
        return confined

    # ---- reading --------------------------------------------------------------

    def read_plans(
        self, session: ErplSession, obj: SapObject, *, incremental: bool, state: Mapping[str, Any]
    ) -> list[ReadPlan]:
        url = str(obj.meta["entity_set_url"])
        args = ["?"]
        if not incremental:
            # A full refresh must not silently resume from a stored delta position.
            args.append("force_full_load := true")
        max_page_size = clamp(self.options.get("max_page_size"), 1, 100_000)
        if max_page_size is not None:
            args.append(f"max_page_size := {max_page_size}")
        sql = f"SELECT * FROM odp_odata_read({', '.join(args)})"
        return [ReadPlan(sql=sql, params=[url], slice_={"entity_set": obj.meta["entity_set"]})]

    # ---- state ----------------------------------------------------------------

    @staticmethod
    def seed_subscription_statements(
        entity_set_url: str, entity_set: str, delta_token: str
    ) -> list[tuple[str, Sequence[Any]]]:
        """Restore a delta token into erpl_web's own subscription table.

        Two statements rather than an upsert: `odp_subscriptions` carries a
        PRIMARY KEY *and* a UNIQUE(service_url, entity_set_name), and DuckDB
        refuses `INSERT OR REPLACE` on a table with more than one unique
        constraint. The delete matches the unique key, because erpl_web's
        `subscription_id` is timestamp-prefixed and changes every run.
        """
        return [
            (
                "DELETE FROM erpl_web.odp_subscriptions WHERE service_url = ? AND entity_set_name = ?",
                [entity_set_url, entity_set],
            ),
            (
                "INSERT INTO erpl_web.odp_subscriptions "
                "(subscription_id, service_url, entity_set_name, secret_name, delta_token, "
                " subscription_status, preference_applied, schema_version) "
                "VALUES (?, ?, ?, NULL, ?, 'active', TRUE, 1)",
                [f"airbyte_{entity_set}", entity_set_url, entity_set, delta_token],
            ),
        ]

    def prepare(self, session: ErplSession, obj: SapObject, state: Mapping[str, Any]) -> None:
        token = state.get("delta_token")
        if not token:
            return
        cursor = session.cursor()
        try:
            # Touch the listing function first so erpl_web creates its schema.
            cursor.execute("SELECT 1 FROM odp_odata_list_subscriptions() LIMIT 1").fetchall()
            # DELETE then INSERT must not be interruptible: a crash between them
            # would leave the stream with no stored position at all.
            cursor.execute("BEGIN TRANSACTION")
            try:
                for sql, params in self.seed_subscription_statements(
                    str(obj.meta["entity_set_url"]), str(obj.meta["entity_set"]), str(token)
                ):
                    cursor.execute(sql, list(params))
                cursor.execute("COMMIT")
            except Exception:
                cursor.execute("ROLLBACK")
                raise
        except Exception as exc:
            raise traced(
                f"Could not restore the ODP delta position for {obj.name}. "
                "Reset the stream to start from a fresh full load",
                exc,
                stream_name=obj.name,
            ) from exc

    def next_state(self, session: ErplSession, obj: SapObject, previous: Mapping[str, Any]) -> Mapping[str, Any]:
        state = dict(previous)
        state["service_url"] = obj.meta["entity_set_url"]
        state["entity_set"] = obj.meta["entity_set"]
        try:
            row = (
                session.cursor()
                .execute(
                    "SELECT delta_token FROM odp_odata_list_subscriptions() "
                    "WHERE service_url = ? AND entity_set_name = ? "
                    "ORDER BY last_updated DESC LIMIT 1",
                    [obj.meta["entity_set_url"], obj.meta["entity_set"]],
                )
                .fetchone()
            )
        except Exception as exc:
            logger.warning("Could not read back the ODP delta token for %s: %s", obj.name, exc)
            return state
        if row and row[0]:
            state["delta_token"] = coerce_value(row[0])
        elif "delta_token" not in state:
            logger.warning(
                "SAP returned no delta token for %s. The next sync will do a full load again; "
                "this usually means the entity set is not delta-enabled.",
                obj.name,
            )
        return state
