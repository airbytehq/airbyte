/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.jobs;

import io.airbyte.db.Database;
import io.airbyte.db.instance.DatabaseMigrator;
import io.airbyte.db.instance.FlywayMigrationDatabase;
import java.io.IOException;

/**
 * Jobs database for jOOQ code generation.
 */
public class JobsFlywayMigrationDatabase extends FlywayMigrationDatabase {

  @Override
  protected Database getAndInitializeDatabase(final String username, final String password, final String connectionString) throws IOException {
    return new JobsDatabaseInstance(username, password, connectionString).getAndInitialize();
  }

  @Override
  protected DatabaseMigrator getDatabaseMigrator(final Database database) {
    return new JobsDatabaseMigrator(database, JobsFlywayMigrationDatabase.class.getSimpleName());
  }

}
