/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.toys;

import io.airbyte.db.Database;
import io.airbyte.db.instance.FlywayDatabaseMigrator;

/**
 * A database migrator for testing purposes only.
 */
public class ToysDatabaseMigrator extends FlywayDatabaseMigrator {

  public static final String DB_IDENTIFIER = "toy";
  public static final String MIGRATION_FILE_LOCATION = "classpath:io/airbyte/db/instance/toys/migrations";

  public ToysDatabaseMigrator(Database database, String migrationRunner) {
    super(database, DB_IDENTIFIER, migrationRunner, MIGRATION_FILE_LOCATION);
  }

}
