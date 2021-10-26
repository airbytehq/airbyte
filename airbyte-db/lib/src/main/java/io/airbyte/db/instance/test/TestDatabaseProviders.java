/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.test;

import com.google.api.client.util.Preconditions;
import io.airbyte.config.Configs;
import io.airbyte.db.Database;
import io.airbyte.db.instance.configs.ConfigsDatabaseTestProvider;
import io.airbyte.db.instance.jobs.JobsDatabaseTestProvider;
import java.io.IOException;
import java.util.Optional;
import org.testcontainers.containers.PostgreSQLContainer;

/**
 * Use this class to create mock databases in unit tests. This class takes care of database
 * initialization and migration.
 */
@SuppressWarnings("OptionalUsedAsFieldOrParameterType")
public class TestDatabaseProviders {

  private final Optional<Configs> configs;
  private final Optional<PostgreSQLContainer<?>> container;
  private boolean runMigration = true;

  public TestDatabaseProviders(final Configs configs) {
    this.configs = Optional.of(configs);
    this.container = Optional.empty();
  }

  public TestDatabaseProviders(final PostgreSQLContainer<?> container) {
    this.configs = Optional.empty();
    this.container = Optional.of(container);
  }

  /**
   * When creating mock databases in unit tests, migration should be run by default. Call this method
   * to turn migration off, which is needed when unit testing migration code.
   */
  public TestDatabaseProviders turnOffMigration() {
    this.runMigration = false;
    return this;
  }

  public Database createNewConfigsDatabase() throws IOException {
    Preconditions.checkArgument(configs.isPresent() || container.isPresent());
    if (configs.isPresent()) {
      final Configs c = configs.get();
      return new ConfigsDatabaseTestProvider(
          c.getConfigDatabaseUser(),
          c.getConfigDatabasePassword(),
          c.getConfigDatabaseUrl())
              .create(runMigration);
    } else {
      final PostgreSQLContainer<?> c = container.get();
      return new ConfigsDatabaseTestProvider(
          c.getUsername(),
          c.getPassword(),
          c.getJdbcUrl())
              .create(runMigration);
    }
  }

  public Database createNewJobsDatabase() throws IOException {
    Preconditions.checkArgument(configs.isPresent() || container.isPresent());
    if (configs.isPresent()) {
      final Configs c = configs.get();
      return new JobsDatabaseTestProvider(
          c.getDatabaseUser(),
          c.getDatabasePassword(),
          c.getDatabaseUrl())
              .create(runMigration);
    } else {
      final PostgreSQLContainer<?> c = container.get();
      return new JobsDatabaseTestProvider(
          c.getUsername(),
          c.getPassword(),
          c.getJdbcUrl())
              .create(runMigration);
    }
  }

}
