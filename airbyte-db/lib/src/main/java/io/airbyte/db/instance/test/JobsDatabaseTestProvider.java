/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.test;

import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.db.instance.development.MigrationDevHelper;
import io.airbyte.db.instance.jobs.JobsDatabaseInstance;
import java.io.IOException;
import javax.sql.DataSource;
import org.flywaydb.core.Flyway;
import org.jooq.SQLDialect;

public class JobsDatabaseTestProvider implements TestDatabaseProvider {

  private final DataSource dataSource;

  public JobsDatabaseTestProvider(final DataSource dataSource) {
    this.dataSource = dataSource;
  }

  @Override
  public Database create(final boolean runMigration) throws IOException {
    final Database jobsDatabase = new JobsDatabaseInstance(Databases.createDslContext(dataSource, SQLDialect.POSTGRES))
        .getAndInitialize();

    if (runMigration) {
      final Flyway migrator = MigrationDevHelper.createMigrator(dataSource, MigrationDevHelper.JOBS_DB_IDENTIFIER);
      migrator.baseline();
      migrator.migrate();
    }

    return jobsDatabase;
  }

}
