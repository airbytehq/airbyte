# Copyright (c) 2026 Albert Wong
# SPDX-License-Identifier: MIT
"""The extraction layer is independent of Airbyte and the particular ADBC driver."""

import os
from contextlib import closing, contextmanager, suppress
from dataclasses import dataclass

import adbc_driver_manager.dbapi as dbapi
import jsonschema

from .conversion import ConversionError, batch_records, schema_to_json


class ConnectorError(RuntimeError):
    """Safe to show to users; never contains raw driver exception text."""


@dataclass(frozen=True)
class Table:
    catalog: str | None
    namespace: str | None
    name: str


def validate_config(config, spec):
    try:
        jsonschema.Draft7Validator(spec).validate(config)
    except jsonschema.ValidationError:
        raise ConnectorError("Invalid connector configuration; check the connection specification.") from None
    mode = config.get("connection_type", "redis")
    schemes = ("redis://", "rediss://") if mode == "redis" else ("grpc://", "grpc+tls://", "grpc+tcp://")
    if not config["uri"].startswith(schemes):
        raise ConnectorError("URI scheme does not match the selected connection type.")
    forbidden = {"uri", "driver", "entrypoint", "adbc.connection.autocommit"}
    if forbidden.intersection(config.get("database_options", {})):
        raise ConnectorError("Database options cannot override connection or transaction settings.")


def _redis_driver_path():
    override = os.environ.get("REDIS_ADBC_LIBRARY")
    if override:
        return override
    from adbc_driver_redis import _driver_path

    return _driver_path()


def connect(config):
    options = dict(config.get("database_options", {}))
    if config.get("connection_type", "redis") == "flight_sql":
        from adbc_driver_flightsql import dbapi as flight

        return flight.connect(config["uri"], db_kwargs=options, autocommit=True)
    options.update(
        {
            "uri": config["uri"],
            "adbc.redis.stream_results": "true",
            "adbc.redis.stream_batch_rows": str(config.get("batch_size", 1024)),
        }
    )
    return dbapi.connect(
        driver=_redis_driver_path(),
        entrypoint="AdbcDriverRedisInit",
        db_kwargs=options,
        autocommit=True,
    )


class AdbcBackend:
    def __init__(self, config, connect_fn=connect):
        self.config = config
        self.connect_fn = connect_fn

    @contextmanager
    def connection(self):
        try:
            with closing(self.connect_fn(self.config)) as connection:
                yield connection
        except (ConnectorError, ConversionError):
            raise
        except Exception:
            # ADBC diagnostics can include credentials, option values and URIs.
            raise ConnectorError(
                "ADBC operation failed. Verify connectivity, permissions, Search support and schema; driver diagnostics were withheld to protect credentials."
            ) from None

    @contextmanager
    def query(self, connection, sql):
        with closing(connection.cursor()) as cursor:
            complete = False
            try:
                cursor.execute(sql)
                with closing(cursor.fetch_record_batch()) as reader:
                    yield reader
                    complete = True
            finally:
                if not complete:
                    with suppress(Exception):
                        cursor.adbc_cancel()

    def tables(self, connection):
        schemas = self.config.get("schemas", ["public"])
        wanted_catalog = self.config.get("catalog")
        result = {}
        with closing(connection.adbc_get_objects(depth="tables")) as reader:
            for batch in reader:
                for catalog in batch.to_pylist():
                    cat = catalog["catalog_name"]
                    if wanted_catalog is not None and cat != wanted_catalog:
                        continue
                    for schema in catalog["catalog_db_schemas"] or []:
                        namespace = schema["db_schema_name"]
                        if (namespace or "") not in schemas:
                            continue
                        for table in schema["db_schema_tables"] or []:
                            if table["table_type"].upper() not in ("TABLE", "BASE TABLE", "VIEW"):
                                continue
                            obj = Table(cat, namespace, table["table_name"])
                            key = (namespace, obj.name)
                            if key in result:
                                raise ConnectorError("Ambiguous stream names across catalogs; configure an exact catalog.")
                            result[key] = obj
        return result

    def schema(self, connection, table):
        return connection.adbc_get_table_schema(table.name, catalog_filter=table.catalog, db_schema_filter=table.namespace)

    def check(self):
        with self.connection() as connection:
            with self.query(connection, "SELECT 1") as reader:
                for _ in reader:
                    pass
            # Also exercise Search-backed metadata, rather than only SELECT 1.
            self.tables(connection)

    def discover(self):
        with self.connection() as connection:
            return [(table, schema_to_json(self.schema(connection, table))) for table in self.tables(connection).values()]

    def read(self, selections):
        with self.connection() as connection:
            tables = self.tables(connection)
            # Validate all selected streams before emitting any records.
            plans = []
            seen = set()
            for namespace, name, selected in selections:
                key = (namespace, name)
                if key in seen or key not in tables:
                    raise ConnectorError("Selected stream is missing or duplicated; rediscover the catalog.")
                seen.add(key)
                table = tables[key]
                schema = self.schema(connection, table)
                properties = schema_to_json(schema)["properties"]
                if not selected or any(field not in properties for field in selected):
                    raise ConnectorError("Selected fields are empty or missing; rediscover the catalog.")
                if any(selected[field] != properties[field] for field in selected):
                    raise ConnectorError("Selected field schema changed; rediscover the catalog.")
                # Preserve source order and push down only the selected columns.
                fields = [field for field in schema if field.name in selected]
                plans.append((table, fields))
            for table, fields in plans:
                target = ".".join(quote(part) for part in (table.catalog, table.namespace, table.name) if part)
                sql = f"SELECT {', '.join(quote(f.name) for f in fields)} FROM {target}"
                with self.query(connection, sql) as reader:
                    if [(f.name, f.type) for f in reader.schema] != [(f.name, f.type) for f in fields]:
                        raise ConnectorError("Query schema changed; rediscover the catalog.")
                    for batch in reader:
                        for record in batch_records(batch):
                            yield table, record


def quote(identifier):
    return '"' + identifier.replace('"', '""') + '"'
