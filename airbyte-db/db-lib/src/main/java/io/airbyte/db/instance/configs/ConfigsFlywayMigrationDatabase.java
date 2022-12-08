/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs;

import io.airbyte.commons.resources.MoreResources;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DatabaseCheckFactory;
import io.airbyte.db.init.DatabaseInitializationException;
import io.airbyte.db.instance.DatabaseConstants;
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
  protected Database getDatabase(final DSLContext dslContext) throws IOException {
    return new Database(dslContext);
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

  @Override
  protected void initializeDatabase(final DSLContext dslContext) throws DatabaseInitializationException, IOException {
    final String initialSchema = MoreResources.readResource(DatabaseConstants.CONFIGS_INITIAL_SCHEMA_PATH);
    DatabaseCheckFactory.createConfigsDatabaseInitializer(dslContext, DatabaseConstants.DEFAULT_CONNECTION_TIMEOUT_MS, initialSchema).initialize();
  }

}
