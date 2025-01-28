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
import pytz
from psycopg2 import extensions, sql


catalog_write_file = "/connector/integration_tests/temp/configured_catalog_copy.json"
catalog_source_file = "/connector/integration_tests/configured_catalog_template.json"
catalog_incremental_write_file = "/connector/integration_tests/temp/incremental_configured_catalog_copy.json"
catalog_incremental_source_file = "/connector/integration_tests/incremental_configured_catalog_template.json"
abnormal_state_write_file = "/connector/integration_tests/temp/abnormal_state_copy.json"
abnormal_state_file = "/connector/integration_tests/abnormal_state_template.json"

secret_config_file = "/connector/secrets/config.json"
secret_active_config_file = "/connector/integration_tests/temp/config_active.json"
secret_config_cdc_file = "/connector/secrets/config_cdc.json"
secret_active_config_cdc_file = "/connector/integration_tests/temp/config_cdc_active.json"

la_timezone = pytz.timezone("America/Los_Angeles")


def connect_to_db() -> extensions.connection:
    with open(secret_config_file) as f:
        secret = json.load(f)

    try:
        conn: extensions.connection = psycopg2.connect(
            dbname=secret["database"], user=secret["username"], password=secret["password"], host=secret["host"], port=secret["port"]
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
        with open(catalog_source_file, "r") as source_file:
            file.write(source_file.read() % schema_name)
    with open(catalog_incremental_write_file, "w") as file:
        with open(catalog_incremental_source_file, "r") as source_file:
            file.write(source_file.read() % schema_name)
    with open(abnormal_state_write_file, "w") as file:
        with open(abnormal_state_file, "r") as source_file:
            file.write(source_file.read() % (schema_name, schema_name))

    with open(secret_config_file) as base_config:
        secret = json.load(base_config)
        secret["schemas"] = [schema_name]
        with open(secret_active_config_file, "w") as f:
            json.dump(secret, f)

    with open(secret_config_cdc_file) as base_config:
        secret = json.load(base_config)
        secret["schemas"] = [schema_name]
        secret["replication_method"]["replication_slot"] = schema_name
        secret["replication_method"]["publication"] = schema_name
        secret["ssl_mode"] = {}
        secret["ssl_mode"]["mode"] = "require"
        with open(secret_active_config_cdc_file, "w") as f:
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
    current_date = datetime.datetime.now(la_timezone).strftime("%Y%m%d")
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{current_date}_{suffix}"


def prepare() -> None:
    schema_name = generate_schema_date_with_suffix()
    print(f"schema_name: {schema_name}")
    with open("./generated_schema.txt", "w") as f:
        f.write(schema_name)


def cdc_insert():
    schema_name = load_schema_name_from_catalog()
    new_records = [("4", "four"), ("5", "five")]
    connection = connect_to_db()
    table_name = "id_and_name_cat"
    if connection:
        insert_records(connection, schema_name, table_name, new_records)
        connection.close()


def setup(with_cdc=False):
    schema_name = load_schema_name_from_catalog()
    write_supporting_file(schema_name)
    table_name = "id_and_name_cat"

    # Define the records to be inserted
    records = [("1", "one"), ("2", "two"), ("3", "three")]

    # Connect to the database
    connection = connect_to_db()

    # Create the schema
    create_schema(connection, schema_name)
    create_table(connection, schema_name, table_name)
    if with_cdc:
        setup_cdc(connection, replication_slot_and_publication_name=schema_name)
    # Insert the records
    insert_records(connection, schema_name, table_name, records)

    # Close the connection
    connection.close()


def replication_slot_existed(connection, replication_slot_name):
    cursor = connection.cursor()
    cursor.execute("SELECT slot_name FROM pg_replication_slots;")
    # Fetch all results
    slots = cursor.fetchall()
    for slot in slots:
        if slot[0] == replication_slot_name:
            return True
    return False


def setup_cdc(connection, replication_slot_and_publication_name):
    cursor = connection.cursor()
    if replication_slot_existed(connection, replication_slot_and_publication_name):
        return
    create_logical_replication_query = sql.SQL("SELECT pg_create_logical_replication_slot({}, 'pgoutput')").format(
        sql.Literal(replication_slot_and_publication_name)
    )
    cursor.execute(create_logical_replication_query)
    alter_table_replica_query = sql.SQL("ALTER TABLE {}.id_and_name_cat REPLICA IDENTITY DEFAULT").format(
        sql.Identifier(replication_slot_and_publication_name)
    )
    cursor.execute(alter_table_replica_query)
    create_publication_query = sql.SQL("CREATE PUBLICATION {} FOR TABLE {}.id_and_name_cat").format(
        sql.Identifier(replication_slot_and_publication_name), sql.Identifier(replication_slot_and_publication_name)
    )
    cursor.execute(create_publication_query)
    connection.commit()


def load_schema_name_from_catalog():
    with open("./generated_schema.txt", "r") as f:
        return f.read()


def delete_cdc_with_prefix(conn, prefix):
    try:
        # Connect to the PostgreSQL database
        cursor = conn.cursor()
        cursor.execute("SELECT slot_name FROM pg_replication_slots;")
        # Fetch all results
        slots = cursor.fetchall()
        for slot in slots:
            if slot[0].startswith(prefix):
                print(f"Start dropping replication slot and publication {slot[0]}")
                drop_replication_slot_query = sql.SQL("SELECT pg_drop_replication_slot({});").format(sql.Literal(slot[0]))
                drop_publication_query = sql.SQL("DROP PUBLICATION {};").format(sql.Identifier(slot[0]))
                cursor.execute(drop_publication_query)
                cursor.execute(drop_replication_slot_query)
                print(f"Dropping {slot[0]} done")
        conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)
    finally:
        if cursor:
            cursor.close()


def delete_schemas_with_prefix(conn, date_prefix):
    try:
        # Connect to the PostgreSQL database
        cursor = conn.cursor()

        # Query to find all schemas that start with the specified date prefix
        query = sql.SQL("""
            SELECT schema_name
            FROM information_schema.schemata
            WHERE schema_name LIKE %s;
        """)

        cursor.execute(query, (f"{date_prefix}%",))
        schemas = cursor.fetchall()

        # Generate and execute DROP SCHEMA statements for each matching schema
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


def teardown() -> None:
    conn = connect_to_db()
    today = datetime.datetime.now(la_timezone)
    yesterday = today - timedelta(days=1)
    formatted_yesterday = yesterday.strftime("%Y%m%d")
    delete_schemas_with_prefix(conn, formatted_yesterday)
    delete_cdc_with_prefix(conn, formatted_yesterday)


def final_teardown() -> None:
    conn = connect_to_db()
    schema_name = load_schema_name_from_catalog()
    print(f"delete schema {schema_name}")
    delete_schemas_with_prefix(conn, schema_name)
    delete_cdc_with_prefix(conn, schema_name)


if __name__ == "__main__":
    command = sys.argv[1]
    if command == "setup":
        setup(with_cdc=False)
    elif command == "setup_cdc":
        setup(with_cdc=True)
    elif command == "teardown":
        teardown()
    elif command == "final_teardown":
        final_teardown()
    elif command == "prepare":
        prepare()
    elif command == "insert":
        cdc_insert()
    else:
        print(f"Unrecognized command {command}.")
        exit(1)
