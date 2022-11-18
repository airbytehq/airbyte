/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.jobs;

import io.airbyte.db.Database;
import io.airbyte.db.factory.FlywayFactory;
import io.airbyte.db.instance.DatabaseConstants;
import io.airbyte.db.instance.FlywayDatabaseMigrator;
import io.airbyte.db.instance.development.MigrationDevCenter;
import javax.sql.DataSource;
import org.flywaydb.core.Flyway;

/**
 * Helper class for migration development. See README for details.
 */
public class JobsDatabaseMigrationDevCenter extends MigrationDevCenter {

  public JobsDatabaseMigrationDevCenter() {
    super("jobs", DatabaseConstants.JOBS_SCHEMA_DUMP_PATH, DatabaseConstants.JOBS_INITIAL_SCHEMA_PATH);
  }

  @Override
  protected FlywayDatabaseMigrator getMigrator(final Database database, final Flyway flyway) {
    return new JobsDatabaseMigrator(database, flyway);
  }

  @Override
  protected Flyway getFlyway(final DataSource dataSource) {
    return FlywayFactory.create(dataSource, getClass().getSimpleName(), JobsDatabaseMigrator.DB_IDENTIFIER,
        JobsDatabaseMigrator.MIGRATION_FILE_LOCATION);
  }

}
