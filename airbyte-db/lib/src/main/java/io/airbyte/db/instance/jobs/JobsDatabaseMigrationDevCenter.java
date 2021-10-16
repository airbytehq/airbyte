/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.jobs;

import io.airbyte.db.Database;
import io.airbyte.db.instance.FlywayDatabaseMigrator;
import io.airbyte.db.instance.development.MigrationDevCenter;
import java.io.IOException;
import org.testcontainers.containers.PostgreSQLContainer;

/**
 * Helper class for migration development. See README for details.
 */
public class JobsDatabaseMigrationDevCenter extends MigrationDevCenter {

  public JobsDatabaseMigrationDevCenter() {
    super("jobs", "src/main/resources/jobs_database/schema_dump.txt");
  }

  @Override
  protected FlywayDatabaseMigrator getMigrator(final Database database) {
    return new JobsDatabaseMigrator(database, JobsDatabaseMigrationDevCenter.class.getSimpleName());
  }

  @Override
  protected Database getDatabase(final PostgreSQLContainer<?> container) throws IOException {
    return new JobsDatabaseInstance(container.getUsername(), container.getPassword(), container.getJdbcUrl()).getAndInitialize();
  }

}
