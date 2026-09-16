#!/usr/bin/env -S uv run --script
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "cryptography",
#   "snowflake-connector-python",
# ]
# ///
import argparse
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

import snowflake.connector
from cryptography.hazmat.primitives import serialization


SCHEMA_PATTERN = re.compile(r"^PROVEFIX_[A-Z0-9_]+$")


def config() -> dict:
    path = Path(os.environ["SNOWFLAKE_CONFIG_FILE"])
    return json.loads(path.read_text())


def validate_schema(name: str) -> str:
    if not SCHEMA_PATTERN.fullmatch(name):
        raise SystemExit(f"schema must match {SCHEMA_PATTERN.pattern} (got {name!r})")
    return name


def quoted_identifier(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def quoted_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def connect(schema: str | None = None):
    settings = config()
    credentials = settings["credentials"]
    private_key = serialization.load_pem_private_key(credentials["private_key"].encode(), password=None)
    private_key_der = private_key.private_bytes(
        serialization.Encoding.DER,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    parameters = {
        "account": settings["host"].removesuffix(".snowflakecomputing.com"),
        "user": credentials["username"],
        "private_key": private_key_der,
        "role": settings["role"],
        "warehouse": settings["warehouse"],
        "database": settings["database"],
        "login_timeout": 30,
        "network_timeout": 60,
    }
    if schema is not None:
        parameters["schema"] = validate_schema(schema)
    return snowflake.connector.connect(**parameters)


def schema_rows(connection, pattern: str) -> list[dict]:
    database = quoted_identifier(config()["database"])
    cursor = connection.cursor()
    try:
        cursor.execute(f"SHOW SCHEMAS LIKE {quoted_literal(pattern)} IN DATABASE {database}")
        columns = [column[0].lower() for column in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    finally:
        cursor.close()


def schema_exists(name: str) -> bool:
    validate_schema(name)
    connection = connect()
    try:
        return any(row["name"].upper() == name.upper() for row in schema_rows(connection, name))
    finally:
        connection.close()


def create_schema(name: str) -> None:
    validate_schema(name)
    connection = connect()
    try:
        cursor = connection.cursor()
        try:
            cursor.execute(f"CREATE SCHEMA {quoted_identifier(name)}")
        finally:
            cursor.close()
    finally:
        connection.close()


def drop_schema(name: str) -> None:
    validate_schema(name)
    connection = connect()
    try:
        cursor = connection.cursor()
        try:
            cursor.execute(f"DROP SCHEMA IF EXISTS {quoted_identifier(name)}")
        finally:
            cursor.close()
    finally:
        connection.close()


def execute_file(path: Path, schema: str) -> None:
    validate_schema(schema)
    connection = connect(schema)
    try:
        connection.execute_string(path.read_text())
    finally:
        connection.close()


def list_schemas(pattern: str, older_than_hours: float | None) -> None:
    if not pattern.startswith("PROVEFIX_"):
        raise SystemExit("schema pattern must start with PROVEFIX_")
    connection = connect()
    try:
        rows = schema_rows(connection, pattern)
    finally:
        connection.close()
    cutoff = None
    if older_than_hours is not None:
        cutoff = datetime.now(timezone.utc).timestamp() - older_than_hours * 3600
    for row in rows:
        created_on = row["created_on"]
        if cutoff is not None:
            if created_on.tzinfo is None:
                created_on = created_on.replace(tzinfo=timezone.utc)
            if created_on.timestamp() > cutoff:
                continue
        print(row["name"], flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("schema-exists", "create-schema", "drop-schema"):
        command_parser = subparsers.add_parser(command)
        command_parser.add_argument("name")
    exec_parser = subparsers.add_parser("exec-file")
    exec_parser.add_argument("path", type=Path)
    exec_parser.add_argument("--schema", required=True)
    list_parser = subparsers.add_parser("list-schemas")
    list_parser.add_argument("--like", required=True)
    list_parser.add_argument("--older-than-hours", type=float)
    args = parser.parse_args()

    if args.command == "schema-exists":
        print("true" if schema_exists(args.name) else "false", flush=True)
    elif args.command == "create-schema":
        create_schema(args.name)
    elif args.command == "drop-schema":
        drop_schema(args.name)
    elif args.command == "exec-file":
        execute_file(args.path, args.schema)
    else:
        list_schemas(args.like, args.older_than_hours)


if __name__ == "__main__":
    main()
