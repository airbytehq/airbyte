# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import datetime
import hashlib
import json
import random
import string
import sys
from contextlib import contextmanager
from datetime import timedelta
from pathlib import Path
from typing import Generator, List, Tuple

import jaydebeapi
import pytz


ROOT = "/connector"
CAT_ROOT = f"{ROOT}/integration_tests"
CAT_GEN_ROOT = f"{CAT_ROOT}/temp"
SECRETS_DIR = f"{ROOT}/secrets"

FULL_REFRESH_CONFIGURED_CATALOG_TEMPLATE = f"{CAT_ROOT}/full-refresh-configured-catalog-template.json"
INCREMENTAL_CONFIGURED_CATALOG_TEMPLATE = f"{CAT_ROOT}/incremental-configured-catalog-template.json"
INCREMENTAL_CDC_CONFIGURED_CATALOG_TEMPLATE = f"{CAT_ROOT}/incremental-cdc-configured-catalog-template.json"
ABNORMAL_STATE_TEMPLATE = f"{CAT_ROOT}/abnormal-state-template.json"
SECRET_ADMIN_CONFIG = f"{SECRETS_DIR}/config.json"
SECRET_ADMIN_CDC_CONFIG = f"{SECRETS_DIR}/config-cdc.json"

FULL_REFRESH_CONFIGURED_CATALOG = f"{CAT_GEN_ROOT}/full-refresh-configured-catalog.json"
INCREMENTAL_CONFIGURED_CATALOG = f"{CAT_GEN_ROOT}/incremental-configured-catalog.json"
INCREMENTAL_CDC_CONFIGURED_CATALOG = f"{CAT_GEN_ROOT}/incremental-cdc-configured-catalog.json"
ABNORMAL_STATE = f"{CAT_GEN_ROOT}/abnormal-state.json"
SECRET_CONFIG = f"{CAT_GEN_ROOT}/temp-user-config.json"
SECRET_CDC_CONFIG = f"{CAT_GEN_ROOT}/temp-user-cdc-config.json"

LA_TZ = pytz.timezone("America/Los_Angeles")

JDBC_DRIVER_CLASS = "oracle.jdbc.OracleDriver"
JDBC_DRIVER_PATH = "./ojdbc11.jar"


@contextmanager
def db_txn(config_path: str) -> Generator[jaydebeapi.Connection, None, None]:
    """
    Opens a connection to the database using the credentials inside the file referenced by config_path.
    The connection is used for a single transaction, which is either committed or rolled back.
    The connection is closed afterwards.
    """
    with open(config_path) as f:
        secret = json.load(f)

    service_name = secret["connection_data"]["service_name"]
    jdbc_url = f"jdbc:oracle:thin:@//{secret['host']}:{secret['port']}/{service_name}"
    try:
        conn = jaydebeapi.connect(
            JDBC_DRIVER_CLASS,
            jdbc_url,
            [secret["username"], secret["password"]],
            JDBC_DRIVER_PATH,
        )
    except Exception as error:
        print(f"Error connecting to the database: {error}")
        sys.exit(1)
    try:
        conn.jconn.setAutoCommit(False)
        print("Connected to the database successfully")
        yield conn
        conn.commit()
        print("Committed database transaction")
    except Exception as error:
        conn.rollback()
        print(f"Rolled back database transaction after error: {error}")
        sys.exit(1)
    finally:
        conn.close()


def insert_records(
    conn: jaydebeapi.Connection,
    schema_name: str,
    table_name: str,
    records: List[Tuple[str, str]],
) -> None:
    with conn.cursor() as cursor:
        try:
            for record in records:
                id, name = record
                sql = f"INSERT INTO {schema_name}.{table_name} (id, name) VALUES ('{id}', '{name}')"
                cursor.execute(sql)
            print("Records inserted successfully")
        except Exception as error:
            print(f"Error inserting records: {error}")


def schema_password(schema_name: str) -> str:
    md5_hash = hashlib.md5()
    md5_hash.update(schema_name.encode("utf-8"))
    return md5_hash.hexdigest()[:12]


CDC_PRIVILEGES = [
    "FLASHBACK ANY TABLE",
    "SELECT ANY TABLE",
    "SELECT_CATALOG_ROLE",
    "EXECUTE_CATALOG_ROLE",
    "SELECT ANY TRANSACTION",
    "LOGMINING",
    "CREATE TABLE",
    "LOCK ANY TABLE",
    "CREATE SEQUENCE",
]


def create_schema(conn: jaydebeapi.Connection, schema_name: str) -> None:
    create_sql = f'CREATE USER {schema_name} IDENTIFIED BY "{schema_password(schema_name)}"'
    grant_sql = f"GRANT CONNECT, RESOURCE, CREATE SESSION TO {schema_name}"
    tablespace_sql = f"ALTER USER {schema_name} DEFAULT TABLESPACE users"
    quota_sql = f"ALTER USER {schema_name} QUOTA 50M ON USERS"
    grant_cdc_sql = f"GRANT {', '.join(CDC_PRIVILEGES)} TO {schema_name}"

    with conn.cursor() as cursor:
        try:
            cursor.execute(create_sql)
            cursor.execute(grant_sql)
            cursor.execute(tablespace_sql)
            cursor.execute(quota_sql)
            cursor.execute(grant_cdc_sql)
            print(f"Schema '{schema_name}' created successfully")
        except Exception as error:
            print(f"Error creating schema: {error}")


def write_supporting_file(schema_name: str, admin_config_path: str, user_config_path: str) -> None:
    print(f"writing schema name to files: {schema_name}")
    Path(CAT_GEN_ROOT).mkdir(parents=False, exist_ok=True)

    with open(FULL_REFRESH_CONFIGURED_CATALOG, "w") as file:
        with open(FULL_REFRESH_CONFIGURED_CATALOG_TEMPLATE, "r") as source_file:
            file.write(source_file.read() % schema_name)
    with open(INCREMENTAL_CONFIGURED_CATALOG, "w") as file:
        with open(INCREMENTAL_CONFIGURED_CATALOG_TEMPLATE, "r") as source_file:
            file.write(source_file.read() % schema_name)
    with open(INCREMENTAL_CDC_CONFIGURED_CATALOG, "w") as file:
        with open(INCREMENTAL_CDC_CONFIGURED_CATALOG_TEMPLATE, "r") as source_file:
            file.write(source_file.read() % schema_name)
    with open(ABNORMAL_STATE, "w") as file:
        with open(ABNORMAL_STATE_TEMPLATE, "r") as source_file:
            file.write(source_file.read() % schema_name)

    with open(admin_config_path) as base_config:
        secret = json.load(base_config)
        secret["username"] = schema_name
        secret["schemas"] = [schema_name]
        secret["password"] = schema_password(schema_name)
        with open(user_config_path, "w") as f:
            json.dump(secret, f)


def create_table(conn: jaydebeapi.Connection, schema_name: str, table_name: str) -> None:
    plsql = f"""
    DECLARE
        table_count INTEGER;
    BEGIN
        SELECT COUNT(*)
        INTO table_count
        FROM all_tables
        WHERE table_name = '{table_name}' AND owner = '{schema_name}';
        IF table_count = 0 THEN
            EXECUTE IMMEDIATE 'CREATE TABLE {schema_name}.{table_name} (id VARCHAR(100) PRIMARY KEY, name VARCHAR(255) NOT NULL)';
        END IF;
    END;
    """
    with conn.cursor() as cursor:
        try:
            cursor.execute(plsql)
            print(f"Table '{schema_name}.{table_name}' created successfully")
        except Exception as error:
            print(f"Error creating table: {error}")


def generate_schema_date_with_suffix() -> str:
    current_date = datetime.datetime.now(LA_TZ).strftime("%Y%m%d")
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"U{current_date}_{suffix}"


def prepare() -> None:
    schema_name = generate_schema_date_with_suffix()
    print(f"schema_name: {schema_name}")
    with open("./generated_schema.txt", "w") as f:
        f.write(schema_name)


def insert(config_path: str) -> None:
    schema_name = load_schema_name_from_catalog()
    new_records = [("4", "four"), ("5", "five")]
    table_name = "id_and_name_cat"
    with db_txn(config_path) as conn:
        insert_records(conn, schema_name, table_name, new_records)


def setup(admin_config_path: str, user_config_path: str) -> None:
    schema_name = load_schema_name_from_catalog()
    write_supporting_file(schema_name, admin_config_path, user_config_path)
    table_name = "id_and_name_cat"

    # Define the records to be inserted
    records = [("1", "one"), ("2", "two"), ("3", "three")]

    # Connect to the database as admin
    with db_txn(admin_config_path) as conn:
        create_schema(conn, schema_name)

    # Connect to the database as non-admin
    with db_txn(user_config_path) as conn:
        create_table(conn, schema_name, table_name)
        insert_records(conn, schema_name, table_name, records)


def load_schema_name_from_catalog():
    with open("./generated_schema.txt", "r") as f:
        return f.read()


def delete_schemas_with_prefix(conn, date_prefix):
    # Query to find all schemas that start with the specified date prefix
    sql = f"SELECT username FROM dba_users WHERE username LIKE '{date_prefix}%'"
    with conn.cursor() as cursor:
        try:
            cursor.execute(sql)
            schemas = cursor.fetchall()

            # Generate and execute DROP USER statements for each matching schema
            for schema in schemas:
                schema_name = schema[0]
                plsql = f"""
                DECLARE
                    user_count INTEGER;
                BEGIN
                    SELECT COUNT(*) INTO user_count FROM dba_users WHERE username = '{schema_name}';
                    IF user_count > 0 THEN
                        EXECUTE IMMEDIATE 'DROP USER {schema_name} CASCADE';
                    END IF;
                END;
                """
                cursor.execute(plsql)
                print(f"Schema {schema_name} has been dropped.")

            conn.commit()
        except Exception as e:
            print(f"An error occurred: {e}")
            sys.exit(1)


def teardown(admin_config_path: str) -> None:
    schema_name = load_schema_name_from_catalog()
    with db_txn(admin_config_path) as conn:
        delete_schemas_with_prefix(conn, schema_name)


def final_teardown() -> None:
    today = datetime.datetime.now(LA_TZ)
    yesterday = today - timedelta(days=1)
    formatted_yesterday = yesterday.strftime("U%Y%m%d")
    with db_txn(SECRET_ADMIN_CONFIG) as conn:
        delete_schemas_with_prefix(conn, formatted_yesterday)
    with db_txn(SECRET_ADMIN_CDC_CONFIG) as conn:
        delete_schemas_with_prefix(conn, formatted_yesterday)


if __name__ == "__main__":
    command = sys.argv[1]
    if command == "setup":
        setup(SECRET_ADMIN_CONFIG, SECRET_CONFIG)
    elif command == "setup_cdc":
        setup(SECRET_ADMIN_CDC_CONFIG, SECRET_CDC_CONFIG)
    elif command == "teardown":
        teardown(SECRET_ADMIN_CONFIG)
    elif command == "teardown_cdc":
        teardown(SECRET_ADMIN_CDC_CONFIG)
    elif command == "final_teardown":
        final_teardown()
    elif command == "prepare":
        prepare()
    elif command == "insert":
        insert(SECRET_ADMIN_CONFIG)
    elif command == "insert_cdc":
        insert(SECRET_ADMIN_CDC_CONFIG)
    else:
        print(f"Unrecognized command {command}.")
        exit(1)
