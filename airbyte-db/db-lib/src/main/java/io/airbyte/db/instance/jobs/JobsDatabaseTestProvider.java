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
  public Database create(final boolean runMigration) throws IOException, DatabaseInitializationException {
    final String initialSchema = MoreResources.readResource(DatabaseConstants.JOBS_INITIAL_SCHEMA_PATH);
    DatabaseCheckFactory.createJobsDatabaseInitializer(dslContext, DatabaseConstants.DEFAULT_CONNECTION_TIMEOUT_MS, initialSchema).initialize();

    final Database jobsDatabase = new Database(dslContext);

    if (runMigration) {
      final DatabaseMigrator migrator = new JobsDatabaseMigrator(
          jobsDatabase, flyway);
      migrator.createBaseline();
      migrator.migrate();
    }

    return jobsDatabase;
  }

}
