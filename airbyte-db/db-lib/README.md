# How to Create a New Database

Check `io.airbyte.db.instance.configs` for example.

## Database Instance
- Create a new package under `io.airbyte.db.instance` with the name of the database.
- Create the database schema enum that defines all tables in the database.
- Write a SQL script that initializes the database.
  - The default path for this file is `resource/<db-name>_database/schema.sql`.
- Implement the `DatabaseInstance` interface that extends from `BaseDatabaseInstance`. This class initializes the database by executing the initialization script.

## Database Migration
- Implement the `DatabaseMigrator` interface that extends from `BaseDatabaseMigrator`. This class will handle the database migration.
- Create a new package `migrations` under the database package. Put all migrations files there.
- Add the migration commands in `build.gradle` for the new database.
  - The three commands are `new<db-name>Migration`, `run<db-name>Migration`, and `dump<db-name>Schema`.

## jOOQ Code Generation
- To setup jOOQ code generation for the new database, refer to [`airbyte-db/jooq`](../jooq/README.md) for details.
- Please do not use any jOOQ generated code in this `lib` module. This is because the `jooq` module that generates the code depends on this one.

# How to Write a Migration
- Run the `newMigration` command to create a new migration file in `io.airbyte.db.instance.<db-name>.migrations`.
  - Configs database: `./gradlew :airbyte-db:db-lib:newConfigsMigration`.
  - Jobs database: `./gradlew :airbyte-db:db-lib:newJobsMigration`.
- Write the migration using [`jOOQ`](https://www.jooq.org/).
- Use the `runMigration` command to apply your newly written migration if you want to test it.
  - Configs database: `./gradlew :airbyte-db:db-lib:runConfigsMigration`.
  - Jobs database: `./gradlew :airbyte-db:db-lib:runJobsMigration`.
- Run the `dumpSchema` command to update the database schema.
  - Configs database: `./gradlew :airbyte-db:db-lib:dumpConfigsSchema`
  - Jobs database: `./gradlew :airbyte-db:db-lib:dumpJobsSchema`

## Migration Filename
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

## Sample Migration File

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

# How to Run a Migration
- Automatic. Migrations will be run automatically in the server. If you prefer to manually run the migration, change `RUN_DATABASE_MIGRATION_ON_STARTUP` to `false` in `.env`.
- API. Call `api/v1/db_migrations/list` to retrieve the current migration status, and call `api/v1/db_migrations/migrate` to run the migrations. Check the API [documentation](https://airbyte-public-api-docs.s3.us-east-2.amazonaws.com/rapidoc-api-docs.html#tag--db_migration) for more details.

# Schema Dump
- The database schema is checked in to the codebase to ensure that we don't accidentally make any schema change.
- The schema dump can be done manually and automatically.
- To dump the schema manually, run the `dumpSchema` command, as mentioned above.
- The `<db-name>DatabaseMigratorTest` dumps the schema automatically for each database. Please remember to check in any change in the schema dump.
