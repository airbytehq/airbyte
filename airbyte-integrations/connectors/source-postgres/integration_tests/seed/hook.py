# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import datetime
from datetime import timedelta
import json
import os
import random
import string
import sys

import psycopg2
from psycopg2 import sql

catalog_write_file = "/connector/integration_tests/configured_catalog_copy.json"
catalog_source_file = "/connector/integration_tests/configured_catalog.json"
catalog_view_write_file = "/connector/integration_tests/configured_catalog_view_copy.json"
catalog_view_source_file = "/connector/integration_tests/configured_catalog_view.json"
catalog_incremental_write_file = "/connector/integration_tests/incremental_configured_catalog_copy.json"
catalog_incremental_source_file = "/connector/integration_tests/incremental_configured_catalog.json"
abnormal_state_write_file = "/connector/integration_tests/abnormal_state_copy.json"
abnormal_state_file = "/connector/integration_tests/abnormal_state.json"

secret_config_file = '/connector/secrets/config.json'

def connect_to_db():
    f = open(secret_config_file)
    secret = json.load(f)

    try:
        # Define connection parameters
        connection = psycopg2.connect(
            dbname=secret["database"],
            user=secret["username"],
            password=secret["password"],
            host=secret["host"],
            port=secret["port"]
        )
        print("Connected to the database successfully")
        return connection
    except Exception as error:
        print(f"Error connecting to the database: {error}")
        return None

def insert_records(connection, schema_name, table_name, records):
    try:
        cursor = connection.cursor()
        insert_query = sql.SQL("""
            INSERT INTO {}.{} (id, name)
            VALUES (%s, %s)
        """).format(sql.Identifier(schema_name), sql.Identifier(table_name))

        for record in records:
            cursor.execute(insert_query, record)

        connection.commit()
        print("Records inserted successfully")
    except Exception as error:
        print(f"Error inserting records: {error}")
        connection.rollback()
    finally:
        cursor.close()

def create_schema(connection, schema_name):
    try:
        cursor = connection.cursor()
        # Create schema
        create_schema_query = sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(sql.Identifier(schema_name))
        cursor.execute(create_schema_query)
        connection.commit()
        print(f"Schema '{schema_name}' created successfully")

    except Exception as error:
        print(f"Error creating schema: {error}")
        connection.rollback()
    finally:
        cursor.close()

def write_supporting_file(schema_name):
    print(f"writting schema name to files: {schema_name}")
    with open(catalog_write_file, "w") as file:
        with open(catalog_source_file, 'r') as source_file:
            file.write(source_file.read() % schema_name)
    with open(catalog_view_write_file, "w") as file:
        with open(catalog_view_source_file, 'r') as source_file:
            file.write(source_file.read() % schema_name)
    with open(catalog_incremental_write_file, "w") as file:
        with open(catalog_incremental_source_file, 'r') as source_file:
            file.write(source_file.read() % schema_name)
    with open(abnormal_state_write_file, "w") as file:
        with open(abnormal_state_file, 'r') as source_file:
            file.write(source_file.read() % (schema_name, schema_name))
    # update configs:
    with open(secret_config_file) as base_config:
      secret = json.load(base_config)
      secret["schemas"] = [schema_name]
      with open(secret_config_file, 'w') as f:
        json.dump(secret, f)

def create_table(connection, schema_name, table_name):
    try:
        cursor = connection.cursor()
        # Create table
        create_table_query = sql.SQL("""
            CREATE TABLE IF NOT EXISTS {}.{} (
                id VARCHAR(100) PRIMARY KEY,
                name VARCHAR(255) NOT NULL
            )
        """).format(sql.Identifier(schema_name), sql.Identifier(table_name))

        cursor.execute(create_table_query)
        connection.commit()
        print(f"Table '{schema_name}.{table_name}' created successfully")

    except Exception as error:
        print(f"Error creating table: {error}")
        connection.rollback()
    finally:
        cursor.close()

def generate_schema_date_with_suffix():
    current_date = datetime.datetime.now().strftime("%Y%m%d")
    suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    return f"{current_date}-{suffix}"

def prepare():
    schema_name = generate_schema_date_with_suffix()
    with open("./generated_schema.txt", "w") as f:
        f.write(schema_name)

def setup():
    schema_name = load_schema_name_from_catalog()
    write_supporting_file(schema_name)
    table_name = "id_and_name_hook"

    # Define the records to be inserted
    records = [
        ('1', 'one'),
        ('2', 'two'),
        ('3', 'three')
    ]

    # Connect to the database
    connection = connect_to_db()

    if connection:
        # Create the schema
        create_schema(connection, schema_name)
        create_table(connection, schema_name, table_name)

        # Insert the records
        insert_records(connection, schema_name, table_name, records)

        # Close the connection
        connection.close()

def load_schema_name_from_catalog():
    with open("./generated_schema.txt", "r") as f:
        return f.read()

def remove_all_write_files():
    print("***removing write files***")
    os.remove(catalog_write_file)
    os.remove(catalog_view_write_file)
    os.remove(catalog_incremental_write_file)
    os.remove(abnormal_state_write_file)

def delete_schemas_with_prefix(conn, date_prefix):
    try:
        # Connect to the PostgreSQL database
        conn.autocommit = True
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

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def teardown():
    connection = connect_to_db()
    today = datetime.datetime.now()
    yesterday = today - timedelta(days=1)
    formatted_yesterday = yesterday.strftime('%y%m%d')
    delete_schemas_with_prefix(connection, formatted_yesterday)
    remove_all_write_files()

if __name__ == "__main__":
    command = sys.argv[1]
    if command == "setup":
        setup()
    elif command == "teardown":
        teardown()
    elif command == "prepare":
        prepare()
