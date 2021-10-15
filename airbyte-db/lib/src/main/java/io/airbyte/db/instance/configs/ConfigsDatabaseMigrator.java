/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs;

import io.airbyte.db.Database;
import io.airbyte.db.instance.FlywayDatabaseMigrator;

public class ConfigsDatabaseMigrator extends FlywayDatabaseMigrator {

  public static final String DB_IDENTIFIER = "configs";
  public static final String MIGRATION_FILE_LOCATION = "classpath:io/airbyte/db/instance/configs/migrations";

  public ConfigsDatabaseMigrator(Database database, String migrationRunner) {
    super(database, DB_IDENTIFIER, migrationRunner, MIGRATION_FILE_LOCATION);
  }

}
