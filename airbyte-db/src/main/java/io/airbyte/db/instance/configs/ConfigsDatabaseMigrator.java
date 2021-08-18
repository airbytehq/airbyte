package io.airbyte.db.instance.configs;

import io.airbyte.db.Database;
import io.airbyte.db.instance.BaseDatabaseMigrator;

public class ConfigsDatabaseMigrator extends BaseDatabaseMigrator {

  public static final String DB_IDENTIFIER = "configs";
  public static final String MIGRATION_FILE_LOCATION = "classpath:io/airbyte/db/instance/configs/migrations";
  public static final String DB_SCHEMA_DUMP = "src/main/resources/configs_database/schema_dump.txt";

  public ConfigsDatabaseMigrator(Database database, String migrationRunner) {
    super(database, DB_IDENTIFIER, migrationRunner, MIGRATION_FILE_LOCATION, DB_SCHEMA_DUMP);
  }

}
