/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.reporter;

import io.airbyte.commons.lang.CloseableShutdownHook;
import io.airbyte.config.Configs;
import io.airbyte.config.EnvConfigs;
import io.airbyte.db.Database;
import io.airbyte.db.check.DatabaseCheckException;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.DatabaseCheckFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.factory.FlywayFactory;
import io.airbyte.db.instance.configs.ConfigsDatabaseMigrator;
import io.airbyte.metrics.lib.MetricClientFactory;
import io.airbyte.metrics.lib.MetricEmittingApps;
import java.lang.invoke.MethodHandles;
import java.util.concurrent.Executors;
import javax.sql.DataSource;
import org.flywaydb.core.Flyway;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
∂
public class ReporterApp {
  private static final Logger log = LoggerFactory.getLogger(MethodHandles.lookup().lookupClass());

  public static Database configDatabase;

  public static void main(final String[] args) throws DatabaseCheckException {
    final Configs configs = new EnvConfigs();

    MetricClientFactory.initialize(MetricEmittingApps.METRICS_REPORTER);

    final DataSource dataSource = DataSourceFactory.create(
        configs.getConfigDatabaseUser(),
        configs.getConfigDatabasePassword(),
        DatabaseDriver.POSTGRESQL.getDriverClassName(),
        configs.getConfigDatabaseUrl());

    try (final DSLContext dslContext = DSLContextFactory.create(dataSource, SQLDialect.POSTGRES)) {

      final Flyway flyway = FlywayFactory.create(dataSource, ReporterApp.class.getSimpleName(),
          ConfigsDatabaseMigrator.DB_IDENTIFIER, ConfigsDatabaseMigrator.MIGRATION_FILE_LOCATION);

      // Ensure that the database resources are closed on application shutdown
      CloseableShutdownHook.registerRuntimeShutdownHook(dataSource, dslContext);

      // Ensure that the Configuration database is available
      DatabaseCheckFactory.createConfigsDatabaseMigrationCheck(dslContext, flyway, configs.getConfigsDatabaseMinimumFlywayMigrationVersion(),
          configs.getConfigsDatabaseInitializationTimeoutMs()).check();

      configDatabase = new Database(dslContext);

      final var toEmits = ToEmit.values();
      final var pollers = Executors.newScheduledThreadPool(toEmits.length);

      log.info("Scheduling {} metrics for emission..", toEmits.length);
      for (final ToEmit toEmit : toEmits) {
        pollers.scheduleAtFixedRate(toEmit.emitRunnable, 0, toEmit.period, toEmit.timeUnit);
      }
    }
  }

}
