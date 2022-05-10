/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs;

import io.airbyte.db.Database;
import io.airbyte.db.instance.DatabaseMigrator;
import io.airbyte.db.instance.FlywayMigrationDatabase;
import java.io.IOException;
import org.flywaydb.core.Flyway;
import org.jooq.DSLContext;

/**
 * Configs database for jOOQ code generation.
 */
public class ConfigsFlywayMigrationDatabase extends FlywayMigrationDatabase {

  @Override
  protected Database getAndInitializeDatabase(final DSLContext dslContext) throws IOException {
    return new ConfigsDatabaseInstance(dslContext).getAndInitialize();
  }

  @Override
  protected DatabaseMigrator getDatabaseMigrator(final Database database, final Flyway flyway) {
    return new ConfigsDatabaseMigrator(database, flyway);
  }

  @Override
  protected String getInstalledBy() {
    return ConfigsFlywayMigrationDatabase.class.getSimpleName();
  }

  @Override
  protected String getDbIdentifier() {
    return ConfigsDatabaseMigrator.DB_IDENTIFIER;
  }

  @Override
  protected String[] getMigrationFileLocations() {
    return new String[] {ConfigsDatabaseMigrator.MIGRATION_FILE_LOCATION};
  }

}
