# How to Create a New Database

Check `io.airbyte.db.instance.configs` for example.

- Create a new package under `io.airbyte.db.instance` with the name of the database.
- Create the database schema enum that defines all tables in the database.
- Write a SQL script that initializes the database.
  - The default path for this file is `resource/<db-name>_database/schema.sql`.
- Implement the `DatabaseInstance` interface that initializes the database by executing the initialization script.
- [Optional] For each table, create a constant class that defines the table and the columns in jooq.
  - This is necessary only if you plan to use jooq to query the table.
