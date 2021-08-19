package io.airbyte.db.instance.toys;

import io.airbyte.db.Database;
import io.airbyte.db.instance.BaseDatabaseMigrator;

/**
 * A database migrator for testing purposes only.
 */
public class ToysDatabaseMigrator extends BaseDatabaseMigrator {

  public static final String DB_IDENTIFIER = "toy";
  public static final String MIGRATION_FILE_LOCATION = "classpath:io/airbyte/db/instance/toys/migrations";
  public static final String DB_SCHEMA_DUMP = "src/test/resources/toys_database/schema_dump.txt";

  public ToysDatabaseMigrator(Database database, String migrationRunner) {
    super(database, DB_IDENTIFIER, migrationRunner, MIGRATION_FILE_LOCATION, DB_SCHEMA_DUMP);
  }

}
