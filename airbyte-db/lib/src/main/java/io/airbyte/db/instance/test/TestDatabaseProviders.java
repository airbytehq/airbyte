/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.test;

import com.google.api.client.util.Preconditions;
import io.airbyte.config.Configs;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import java.io.IOException;
import java.util.Optional;
import javax.sql.DataSource;
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
      final DataSource dataSource = Databases.dataSourceBuilder()
          .withUsername(c.getConfigDatabaseUser())
          .withPassword(c.getConfigDatabasePassword())
          .withJdbcUrl(c.getConfigDatabaseUrl())
          .build();
      return new ConfigsDatabaseTestProvider(dataSource).create(runMigration);
    } else {
      final PostgreSQLContainer<?> c = container.get();
      final DataSource dataSource = Databases.dataSourceBuilder()
          .withUsername(c.getUsername())
          .withPassword(c.getPassword())
          .withJdbcUrl(c.getJdbcUrl())
          .build();
      return new ConfigsDatabaseTestProvider(dataSource).create(runMigration);
    }
  }

  public Database createNewJobsDatabase() throws IOException {
    Preconditions.checkArgument(configs.isPresent() || container.isPresent());
    if (configs.isPresent()) {
      final Configs c = configs.get();
      final DataSource dataSource = Databases.dataSourceBuilder()
          .withUsername(c.getConfigDatabaseUser())
          .withPassword(c.getConfigDatabasePassword())
          .withJdbcUrl(c.getConfigDatabaseUrl())
          .build();
      return new JobsDatabaseTestProvider(dataSource).create(runMigration);
    } else {
      final PostgreSQLContainer<?> c = container.get();
      final DataSource dataSource = Databases.dataSourceBuilder()
          .withUsername(c.getUsername())
          .withPassword(c.getPassword())
          .withJdbcUrl(c.getJdbcUrl())
          .build();
      return new JobsDatabaseTestProvider(dataSource).create(runMigration);
    }
  }

}
