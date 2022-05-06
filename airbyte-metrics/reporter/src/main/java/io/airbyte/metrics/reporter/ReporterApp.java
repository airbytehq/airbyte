/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.reporter;

import io.airbyte.commons.lang.CloseableShutdownHook;
import io.airbyte.config.Configs;
import io.airbyte.config.EnvConfigs;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.instance.configs.ConfigsDatabaseInstance;
import io.airbyte.metrics.lib.DatadogClientConfiguration;
import io.airbyte.metrics.lib.DogStatsDMetricSingleton;
import io.airbyte.metrics.lib.MetricEmittingApps;
import java.io.IOException;
import java.util.concurrent.Executors;
import javax.sql.DataSource;
import lombok.extern.slf4j.Slf4j;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;

@Slf4j
public class ReporterApp {

  public static Database configDatabase;

  public static void main(final String[] args) throws IOException {
    final Configs configs = new EnvConfigs();

    DogStatsDMetricSingleton.initialize(MetricEmittingApps.METRICS_REPORTER, new DatadogClientConfiguration(configs));

    final DataSource dataSource = DataSourceFactory.create(
        configs.getConfigDatabaseUser(),
        configs.getConfigDatabasePassword(),
        DatabaseDriver.POSTGRESQL.getDriverClassName(),
        configs.getConfigDatabaseUrl());

    try (final DSLContext dslContext = DSLContextFactory.create(dataSource, SQLDialect.POSTGRES)) {

      // Ensure that the database resources are closed on application shutdown
      CloseableShutdownHook.registerRuntimeShutdownHook(dataSource, dslContext);

      configDatabase = new ConfigsDatabaseInstance(dslContext)
          .getInitialized();

      final var toEmits = ToEmit.values();
      final var pollers = Executors.newScheduledThreadPool(toEmits.length);

      log.info("Scheduling {} metrics for emission..", toEmits.length);
      for (final ToEmit toEmit : toEmits) {
        pollers.scheduleAtFixedRate(toEmit.emitRunnable, 0, toEmit.period, toEmit.timeUnit);
      }
    }
  }

}
