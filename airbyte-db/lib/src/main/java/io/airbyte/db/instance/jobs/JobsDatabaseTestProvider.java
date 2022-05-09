/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.jobs;

import io.airbyte.db.Database;
import io.airbyte.db.instance.DatabaseMigrator;
import io.airbyte.db.instance.test.TestDatabaseProvider;
import java.io.IOException;
import org.flywaydb.core.Flyway;
import org.jooq.DSLContext;

public class JobsDatabaseTestProvider implements TestDatabaseProvider {

  private final DSLContext dslContext;
  private final Flyway flyway;

  public JobsDatabaseTestProvider(final DSLContext dslContext, final Flyway flyway) {
    this.dslContext = dslContext;
    this.flyway = flyway;
  }

  @Override
  public Database create(final boolean runMigration) throws IOException {
    final Database jobsDatabase = new JobsDatabaseInstance(dslContext)
        .getAndInitialize();

    if (runMigration) {
      final DatabaseMigrator migrator = new JobsDatabaseMigrator(
          jobsDatabase, flyway);
      migrator.createBaseline();
      migrator.migrate();
    }

    return jobsDatabase;
  }

}
