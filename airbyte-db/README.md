# How to Create a New Database

Check `io.airbyte.db.instance.configs` for example.

## Database Instance
- Create a new package under `io.airbyte.db.instance` with the name of the database.
- Create the database schema enum that defines all tables in the database.
- Write a SQL script that initializes the database.
  - The default path for this file is `resource/<db-name>_database/schema.sql`.
- Implement the `DatabaseInstance` interface that extends from `BaseDatabaseInstance`. This class initializes the database by executing the initialization script.
- [Optional] For each table, create a constant class that defines the table and the columns in jooq.
  - This is necessary only if you plan to use jooq to query the table.

## Database Migration
- Implement the `DatabaseMigrator` interface that extends from `BaseDatabaseMigrator`. This class will handle the database migration.
- Create a new package `migrations` under the database package. Put all migrations files there.

# How to Write a Migration
- Create a migration file under `io.airbyte.db.instance.<db-name>.migrations`.
- This file should extend from `BaseJavaMigration`.
- The name of the file should follow this pattern: `V(version)__(migration_description_in_snake_case).java`.
  - This pattern is mandatory for Flyway to correctly locate and sort the migrations.
  - The first part is `V`, which denotes for *versioned* migration.
  - The second part is a version string with this pattern: `<major>_<minor>_<patch>_<id>`.
    - The `major`, `minor`, and `patch` should match that of the Airbyte version.
    - The `id` should start from `001` for each `<major>_<minor>_<patch>` combination.
    - Example version: `0_29_9_001`
  - The third part is a double underscore separator `__`.
  - The fourth part is a brief description in snake case. Only the first letter should be capitalized for consistency. 
  - See original Flyway [documentation](https://flywaydb.org/documentation/concepts/migrations#naming-1) for more details.

Sample migration file:

```java
/**
 * This migration add an "active" column to the "airbyte_configs" table.
 * This column is nullable, and default to {@code true}.
 */
public class V0_29_9_001__Add_active_column extends BaseJavaMigration {

  @Override
  public void migrate(Context context) throws Exception {
    DSL.using(context.getConnection()).alterTable("airbyte_configs")
        .addColumn(field("active", SQLDataType.BOOLEAN.defaultValue(true).nullable(true)))
        .execute();
  }

}
```

- You can test the migration by running the `runMigration` method in `<db-name>DatabaseMigrationTest`. After running this method, you can see the database schema change in the `resources/<db-name>_databases/schema_dump.txt` file.
  - For the `configs` database, the file is `ConfigsDatabaseMigrationTest.java`.
  - This method is for dev testing only. It is not run by CI.
- This test file also has a `testSchemaDump` method that is run by CI. It will dump the database schema automatically. Please remember to check in any change in the schema dump. In this way, we can be sure that there is no unexpected schema changes caused by any new migration.

# How to Run a Migration
- Automatic. Migrations will be run automatically in the server. If you prefer to manually run the migration, change `RUN_FLYWAY_MIGRATION` to `false` in `.env`.
- UI. You can navigate to `/settings/db-migrations` and run the migrations for each database on the UI.
- API. Call `api/v1/db_migrations/info` to retrieve the current migration status, and call `api/v1/db_migrations/migrate` to run the migrations. Check the API [documentation](https://airbyte-public-api-docs.s3.us-east-2.amazonaws.com/rapidoc-api-docs.html#tag--db_migration) for more details.
