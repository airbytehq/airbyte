/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.jobs;

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
 * Jobs database for jOOQ code generation.
 */
public class JobsFlywayMigrationDatabase extends FlywayMigrationDatabase {

  @Override
  protected Database getDatabase(final DSLContext dslContext) {
    return new Database(dslContext);
  }

  @Override
  protected DatabaseMigrator getDatabaseMigrator(final Database database, final Flyway flyway) {
    return new JobsDatabaseMigrator(database, flyway);
  }

  @Override
  protected String getInstalledBy() {
    return JobsFlywayMigrationDatabase.class.getSimpleName();
  }

  @Override
  protected String getDbIdentifier() {
    return JobsDatabaseMigrator.DB_IDENTIFIER;
  }

  @Override
  protected String[] getMigrationFileLocations() {
    return new String[] {JobsDatabaseMigrator.MIGRATION_FILE_LOCATION};
  }

  @Override
  protected void initializeDatabase(final DSLContext dslContext) throws DatabaseInitializationException, IOException {
    final String initialSchema = MoreResources.readResource(DatabaseConstants.JOBS_INITIAL_SCHEMA_PATH);
    DatabaseCheckFactory.createJobsDatabaseInitializer(dslContext, DatabaseConstants.DEFAULT_CONNECTION_TIMEOUT_MS, initialSchema).initialize();
  }

}
