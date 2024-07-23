# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import datetime
import json
import random
import string
import sys
from datetime import timedelta
from pathlib import Path
from typing import List, Tuple

import psycopg2
from psycopg2 import extensions, sql

catalog_write_file = "/connector/integration_tests/temp/configured_catalog_copy.json"
catalog_source_file = "/connector/integration_tests/configured_catalog_template.json"
catalog_incremental_write_file = "/connector/integration_tests/temp/incremental_configured_catalog_copy.json"
catalog_incremental_source_file = "/connector/integration_tests/incremental_configured_catalog_template.json"
abnormal_state_write_file = "/connector/integration_tests/temp/abnormal_state_copy.json"
abnormal_state_file = "/connector/integration_tests/abnormal_state_template.json"

secret_config_file = '/connector/secrets/config.json'
secret_active_config_file = '/connector/integration_tests/config_active.json'

def connect_to_db() -> extensions.connection:
    with open(secret_config_file) as f:
        secret = json.load(f)

    try:
        conn: extensions.connection = psycopg2.connect(
            dbname=secret["database"],
            user=secret["username"],
            password=secret["password"],
            host=secret["host"],
            port=secret["port"]
        )
        print("Connected to the database successfully")
        return conn
    except Exception as error:
        print(f"Error connecting to the database: {error}")
        sys.exit(1)

def insert_records(conn: extensions.connection, schema_name: str, table_name: str, records: List[Tuple[str, str]]) -> None:
    try:
        cursor = conn.cursor()
        insert_query = sql.SQL("""
            INSERT INTO {}.{} (id, name)
            VALUES (%s, %s) ON CONFLICT DO NOTHING
        """).format(sql.Identifier(schema_name), sql.Identifier(table_name))

        for record in records:
            cursor.execute(insert_query, record)

        conn.commit()
        print("Records inserted successfully")
    except Exception as error:
        print(f"Error inserting records: {error}")
        conn.rollback()
    finally:
        cursor.close()

def create_schema(conn: extensions.connection, schema_name: str) -> None:
    try:
        cursor = conn.cursor()
        create_schema_query = sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(sql.Identifier(schema_name))
        cursor.execute(create_schema_query)
        conn.commit()
        print(f"Schema '{schema_name}' created successfully")
    except Exception as error:
        print(f"Error creating schema: {error}")
        conn.rollback()
    finally:
        cursor.close()

def write_supporting_file(schema_name: str) -> None:
    print(f"writing schema name to files: {schema_name}")
    Path("/connector/integration_tests/temp").mkdir(parents=False, exist_ok=True)

    with open(catalog_write_file, "w") as file:
        with open(catalog_source_file, 'r') as source_file:
            file.write(source_file.read() % schema_name)
    with open(catalog_incremental_write_file, "w") as file:
        with open(catalog_incremental_source_file, 'r') as source_file:
            file.write(source_file.read() % schema_name)
    with open(abnormal_state_write_file, "w") as file:
        with open(abnormal_state_file, 'r') as source_file:
            file.write(source_file.read() % (schema_name, schema_name))

    with open(secret_config_file) as base_config:
        secret = json.load(base_config)
        secret["schemas"] = [schema_name]
        with open(secret_active_config_file, 'w') as f:
            json.dump(secret, f)

def create_table(conn: extensions.connection, schema_name: str, table_name: str) -> None:
    try:
        cursor = conn.cursor()
        create_table_query = sql.SQL("""
            CREATE TABLE IF NOT EXISTS {}.{} (
                id VARCHAR(100) PRIMARY KEY,
                name VARCHAR(255) NOT NULL
            )
        """).format(sql.Identifier(schema_name), sql.Identifier(table_name))

        cursor.execute(create_table_query)
        conn.commit()
        print(f"Table '{schema_name}.{table_name}' created successfully")
    except Exception as error:
        print(f"Error creating table: {error}")
        conn.rollback()
    finally:
        cursor.close()

def generate_schema_date_with_suffix() -> str:
    current_date = datetime.datetime.now().strftime("%Y%m%d")
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{current_date}-{suffix}"

def prepare() -> None:
    schema_name = generate_schema_date_with_suffix()
    with open("./generated_schema.txt", "w") as f:
        f.write(schema_name)

def setup() -> None:
    schema_name = load_schema_name_from_catalog()
    write_supporting_file(schema_name)
    table_name = "id_and_name_cat"

    records = [
        ('1', 'one'),
        ('2', 'two'),
        ('3', 'three')
    ]

    conn = connect_to_db()

    if conn:
        create_schema(conn, schema_name)
        create_table(conn, schema_name, table_name)
        insert_records(conn, schema_name, table_name, records)
        conn.close()

def load_schema_name_from_catalog() -> str:
    with open("./generated_schema.txt", "r") as f:
        return f.read()

def delete_schemas_with_prefix(conn: extensions.connection, date_prefix: str) -> None:
    try:
        cursor = conn.cursor()
        query = sql.SQL("""
            SELECT schema_name
            FROM information_schema.schemata
            WHERE schema_name LIKE %s;
        """)

        cursor.execute(query, (f"{date_prefix}%",))
        schemas = cursor.fetchall()

        for schema in schemas:
            drop_query = sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE;").format(sql.Identifier(schema[0]))
            cursor.execute(drop_query)
            print(f"Schema {schema[0]} has been dropped.")

        conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()

def teardown() -> None:
    conn = connect_to_db()
    today = datetime.datetime.now()
    yesterday = today - timedelta(days=1)
    formatted_yesterday = yesterday.strftime('%Y%m%d')
    print(f"formatted_yesterday: {formatted_yesterday}")
    delete_schemas_with_prefix(conn, formatted_yesterday)

if __name__ == "__main__":
    command = sys.argv[1]
    if command == "setup":
        setup()
    elif command == "teardown":
        teardown()
    elif command == "prepare":
        prepare()
    else:
        ra
