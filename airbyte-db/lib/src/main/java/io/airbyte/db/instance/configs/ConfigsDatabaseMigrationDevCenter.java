/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs;

import io.airbyte.db.Database;
import io.airbyte.db.instance.FlywayDatabaseMigrator;
import io.airbyte.db.instance.development.MigrationDevCenter;
import java.io.IOException;
import org.testcontainers.containers.PostgreSQLContainer;

/**
 * Helper class for migration development. See README for details.
 */
public class ConfigsDatabaseMigrationDevCenter extends MigrationDevCenter {

  public ConfigsDatabaseMigrationDevCenter() {
    super("configs", "src/main/resources/configs_database/schema_dump.txt");
  }

  @Override
  protected FlywayDatabaseMigrator getMigrator(Database database) {
    return new ConfigsDatabaseMigrator(database, ConfigsDatabaseMigrationDevCenter.class.getSimpleName());
  }

  @Override
  protected Database getDatabase(PostgreSQLContainer<?> container) throws IOException {
    return new ConfigsDatabaseInstance(container.getUsername(), container.getPassword(), container.getJdbcUrl()).getAndInitialize();
  }

}
