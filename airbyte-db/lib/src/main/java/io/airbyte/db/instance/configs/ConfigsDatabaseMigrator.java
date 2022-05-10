/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs;

import io.airbyte.db.Database;
import io.airbyte.db.instance.FlywayDatabaseMigrator;
import org.flywaydb.core.Flyway;

public class ConfigsDatabaseMigrator extends FlywayDatabaseMigrator {

  public static final String DB_IDENTIFIER = "configs";
  public static final String MIGRATION_FILE_LOCATION = "classpath:io/airbyte/db/instance/configs/migrations";

  public ConfigsDatabaseMigrator(final Database database, final Flyway flyway) {
    super(database, flyway);
  }

}
