import psycopg2
from psycopg2 import sql
import datetime
import random
import string

def connect_to_db():
    try:
        # Define connection parameters
        connection = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="b{;v|l]qxBD~fYJ`",
            host="34.23.30.27",
            port="5432"
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

def create_table(connection, schema_name, table_name):
    try:
        cursor = connection.cursor()
        # Create table
        create_table_query = sql.SQL("""
            CREATE TABLE IF NOT EXISTS {}.{} (
                id INT PRIMARY KEY,
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

def generate_date_with_suffix():
    current_date = datetime.datetime.now().strftime("%Y%m%d")
    suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    return f"{current_date}-{suffix}"

def main():
    schema_name = generate_date_with_suffix()
    table_name = "id_and_name"

    # Define the records to be inserted
    records = [
        (1, 'value1_2'),
        (2, 'value2_2'),
        (3, 'value3_2')
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

if __name__ == "__main__":
    main()
