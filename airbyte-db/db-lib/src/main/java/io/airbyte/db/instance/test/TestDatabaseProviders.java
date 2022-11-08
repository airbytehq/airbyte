/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.test;

import io.airbyte.db.Database;
import io.airbyte.db.factory.FlywayFactory;
import io.airbyte.db.init.DatabaseInitializationException;
import io.airbyte.db.instance.configs.ConfigsDatabaseMigrator;
import io.airbyte.db.instance.configs.ConfigsDatabaseTestProvider;
import io.airbyte.db.instance.jobs.JobsDatabaseMigrator;
import io.airbyte.db.instance.jobs.JobsDatabaseTestProvider;
import java.io.IOException;
import javax.sql.DataSource;
import org.flywaydb.core.Flyway;
import org.jooq.DSLContext;

/**
 * Use this class to create mock databases in unit tests. This class takes care of database
 * initialization and migration.
 */
@SuppressWarnings("OptionalUsedAsFieldOrParameterType")
public class TestDatabaseProviders {

  private final DataSource dataSource;
  private final DSLContext dslContext;
  private boolean runMigration = true;

  public TestDatabaseProviders(final DataSource dataSource, final DSLContext dslContext) {
    this.dataSource = dataSource;
    this.dslContext = dslContext;
  }

  /**
   * When creating mock databases in unit tests, migration should be run by default. Call this method
   * to turn migration off, which is needed when unit testing migration code.
   */
  public TestDatabaseProviders turnOffMigration() {
    this.runMigration = false;
    return this;
  }

  public Database createNewConfigsDatabase() throws IOException, DatabaseInitializationException {
    final Flyway flyway = FlywayFactory.create(dataSource, ConfigsDatabaseTestProvider.class.getSimpleName(), ConfigsDatabaseMigrator.DB_IDENTIFIER,
        ConfigsDatabaseMigrator.MIGRATION_FILE_LOCATION);
    return new ConfigsDatabaseTestProvider(dslContext, flyway)
        .create(runMigration);
  }

  public Database createNewJobsDatabase() throws IOException, DatabaseInitializationException {
    final Flyway flyway = FlywayFactory.create(dataSource, JobsDatabaseTestProvider.class.getSimpleName(), JobsDatabaseMigrator.DB_IDENTIFIER,
        JobsDatabaseMigrator.MIGRATION_FILE_LOCATION);
    return new JobsDatabaseTestProvider(dslContext, flyway)
        .create(runMigration);
  }

}
