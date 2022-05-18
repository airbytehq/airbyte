/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.jobs;

import io.airbyte.db.Database;
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
  protected Database getAndInitializeDatabase(final DSLContext dslContext) throws IOException {
    return new JobsDatabaseInstance(dslContext).getAndInitialize();
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

}
