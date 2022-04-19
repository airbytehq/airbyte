/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs;

import io.airbyte.db.Database;
import io.airbyte.db.instance.DatabaseMigrator;
import io.airbyte.db.instance.FlywayMigrationDatabase;
import java.io.IOException;

/**
 * Configs database for jOOQ code generation.
 */
public class ConfigsFlywayMigrationDatabase extends FlywayMigrationDatabase {

  @Override
  protected Database getAndInitializeDatabase(final String username, final String password, final String connectionString) throws IOException {
    return new ConfigsDatabaseInstance(username, password, connectionString).getAndInitialize();
  }

  @Override
  protected DatabaseMigrator getDatabaseMigrator(final Database database) {
    return new ConfigsDatabaseMigrator(database, ConfigsFlywayMigrationDatabase.class.getSimpleName());
  }

}
