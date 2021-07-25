# How to Create a New Database

- Database schema
  - This is an enum that defines all tables in the database.
  - Add it under the `schema` package that implements the `DatabaseSchema` interface.
- Database initialization script
  - This SQL script defines how the database will be initialized.
  - The default path for this file is `resource/<db-name>_database/schema.sql`.
- Database instance
  - This class initialize a database by executing the initialization script.
  - Add it under the `instance` package that implements the `DatabaseInstance` interface.
 