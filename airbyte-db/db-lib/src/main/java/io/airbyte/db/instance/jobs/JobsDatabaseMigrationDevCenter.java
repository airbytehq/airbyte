/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.jobs;

import io.airbyte.db.Database;
import io.airbyte.db.factory.FlywayFactory;
import io.airbyte.db.instance.FlywayDatabaseMigrator;
import io.airbyte.db.instance.development.MigrationDevCenter;
import javax.sql.DataSource;
import org.flywaydb.core.Flyway;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.ext.ScriptUtils;
import org.testcontainers.jdbc.JdbcDatabaseDelegate;

/**
 * Helper class for migration development. See README for details.
 */
public class JobsDatabaseMigrationDevCenter extends MigrationDevCenter {

  public JobsDatabaseMigrationDevCenter() {
    super("jobs", "src/main/resources/jobs_database/schema_dump.txt");
  }

  @Override
  protected FlywayDatabaseMigrator getMigrator(final Database database, final Flyway flyway) {
    return new JobsDatabaseMigrator(database, flyway);
  }

  @Override
  protected void initializeDatabase(final PostgreSQLContainer<?> container) {
    final var containerDelegate = new JdbcDatabaseDelegate(container, "");
    ScriptUtils.runInitScript(containerDelegate, "jobs_database/schema.sql");
  }

  @Override
  protected Flyway getFlyway(final DataSource dataSource) {
    return FlywayFactory.create(dataSource, getClass().getSimpleName(), JobsDatabaseMigrator.DB_IDENTIFIER,
        JobsDatabaseMigrator.MIGRATION_FILE_LOCATION);
  }

}
