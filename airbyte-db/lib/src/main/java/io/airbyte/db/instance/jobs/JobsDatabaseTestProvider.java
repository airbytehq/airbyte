/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.jobs;

import io.airbyte.db.Database;
import io.airbyte.db.instance.DatabaseMigrator;
import io.airbyte.db.instance.test.TestDatabaseProvider;
import java.io.IOException;

public class JobsDatabaseTestProvider implements TestDatabaseProvider {

  private final String user;
  private final String password;
  private final String jdbcUrl;

  public JobsDatabaseTestProvider(String user, String password, String jdbcUrl) {
    this.user = user;
    this.password = password;
    this.jdbcUrl = jdbcUrl;
  }

  @Override
  public Database create(final boolean runMigration) throws IOException {
    final Database jobsDatabase = new JobsDatabaseInstance(user, password, jdbcUrl)
        .getAndInitialize();

    if (runMigration) {
      final DatabaseMigrator migrator = new JobsDatabaseMigrator(
          jobsDatabase,
          JobsDatabaseTestProvider.class.getSimpleName());
      migrator.createBaseline();
      migrator.migrate();
    }

    return jobsDatabase;
  }

}
