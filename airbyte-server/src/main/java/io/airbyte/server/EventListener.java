/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server;

import io.airbyte.commons.lang.CloseableShutdownHook;
import io.airbyte.config.Configs;
import io.airbyte.config.EnvConfigs;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.FlywayFactory;
import io.airbyte.db.instance.configs.ConfigsDatabaseMigrator;
import io.airbyte.db.instance.jobs.JobsDatabaseMigrator;
import io.airbyte.server.handlers.DbMigrationHandler;
import io.micronaut.runtime.event.ApplicationStartupEvent;
import io.micronaut.scheduling.TaskExecutors;
import io.micronaut.scheduling.annotation.ExecuteOn;
import jakarta.inject.Singleton;
import java.sql.Connection;
import javax.sql.DataSource;
import lombok.extern.slf4j.Slf4j;
import org.flywaydb.core.Flyway;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.jooq.impl.DSL;

@Singleton
@Slf4j
public class EventListener {

  private static final String DRIVER_CLASS_NAME = "org.postgresql.Driver";

  @io.micronaut.runtime.event.annotation.EventListener
  @ExecuteOn(TaskExecutors.IO)
  @SuppressWarnings({"PMD.AvoidCatchingThrowable", "PMD.DoNotTerminateVM"})
  public void startEmitters(final ApplicationStartupEvent event) {
    try {
      final Configs configs = new EnvConfigs();

      final DataSource configDataSource =
          DataSourceFactory.create(configs.getConfigDatabaseUser(), configs.getConfigDatabasePassword(), DRIVER_CLASS_NAME,
              configs.getConfigDatabaseUrl());
      final DataSource jobsDataSource = DataSourceFactory.create(configs.getDatabaseUser(), configs.getDatabasePassword(), DRIVER_CLASS_NAME,
          configs.getDatabaseUrl());

      // Manual configuration that will be replaced by Dependency Injection in the future
      try (final Connection configsConnection = configDataSource.getConnection();
          final Connection jobsConnection = jobsDataSource.getConnection()) {
        final DSLContext configsDslContext = DSL.using(configsConnection, SQLDialect.POSTGRES);
        final DSLContext jobsDslContext = DSL.using(jobsConnection, SQLDialect.POSTGRES);

        // Ensure that the database resources are closed on application shutdown
        CloseableShutdownHook.registerRuntimeShutdownHook(configsConnection, jobsConnection, configsDslContext, jobsDslContext);

        final Flyway configsFlyway = FlywayFactory.create(configDataSource, DbMigrationHandler.class.getSimpleName(),
            ConfigsDatabaseMigrator.DB_IDENTIFIER, ConfigsDatabaseMigrator.MIGRATION_FILE_LOCATION);
        final Flyway jobsFlyway = FlywayFactory.create(jobsDataSource, DbMigrationHandler.class.getSimpleName(), JobsDatabaseMigrator.DB_IDENTIFIER,
            JobsDatabaseMigrator.MIGRATION_FILE_LOCATION);

        ServerApp.getServer(new ServerFactory.Api(), configs, configsDslContext, configsFlyway, jobsDslContext, jobsFlyway).start();
      }
    } catch (final Throwable e) {
      log.error("Server failed", e);
      System.exit(1); // so the app doesn't hang on background thread
    }
  }

}
