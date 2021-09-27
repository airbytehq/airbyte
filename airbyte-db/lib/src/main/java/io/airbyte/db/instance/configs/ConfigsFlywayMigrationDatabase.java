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

  public ConfigsFlywayMigrationDatabase() {
    super("src/main/resources/configs_database/schema_dump.txt");
  }

  @Override
  protected Database getAndInitializeDatabase(String username, String password, String connectionString) throws IOException {
    return new ConfigsDatabaseInstance(username, password, connectionString).getAndInitialize();
  }

  @Override
  protected DatabaseMigrator getDatabaseMigrator(Database database) {
    return new ConfigsDatabaseMigrator(database, ConfigsFlywayMigrationDatabase.class.getSimpleName());
  }

}
