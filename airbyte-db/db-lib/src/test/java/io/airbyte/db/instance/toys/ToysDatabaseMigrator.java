/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.toys;

import io.airbyte.db.Database;
import io.airbyte.db.instance.FlywayDatabaseMigrator;
import org.flywaydb.core.Flyway;

/**
 * A database migrator for testing purposes only.
 */
public class ToysDatabaseMigrator extends FlywayDatabaseMigrator {

  public static final String DB_IDENTIFIER = "toy";
  public static final String MIGRATION_FILE_LOCATION = "classpath:io/airbyte/db/instance/toys/migrations";

  public ToysDatabaseMigrator(final Database database, final Flyway flyway) {
    super(database, flyway);
  }

  @Override
  protected String getDisclaimer() {
    return "";
  }

}
