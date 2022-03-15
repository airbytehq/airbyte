/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.reporter;

import io.airbyte.config.Configs;
import io.airbyte.config.EnvConfigs;
import io.airbyte.db.Database;
import io.airbyte.db.instance.configs.ConfigsDatabaseInstance;
import io.airbyte.metrics.lib.DatadogClientConfiguration;
import io.airbyte.metrics.lib.DogStatsDMetricSingleton;
import io.airbyte.metrics.lib.MetricEmittingApps;
import java.io.IOException;
import java.util.concurrent.Executors;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class ReporterApp {

  public static Database configDatabase;

  public static void main(final String[] args) throws IOException {
    final Configs configs = new EnvConfigs();

    DogStatsDMetricSingleton.initialize(MetricEmittingApps.METRICS_REPORTER, new DatadogClientConfiguration(configs));

    configDatabase = new ConfigsDatabaseInstance(
        configs.getConfigDatabaseUser(),
        configs.getConfigDatabasePassword(),
        configs.getConfigDatabaseUrl())
            .getInitialized();

    final var toEmits = ToEmit.values();
    final var pollers = Executors.newScheduledThreadPool(toEmits.length);

    log.info("Scheduling {} metrics for emission..", toEmits.length);
    for (ToEmit toEmit : toEmits) {
      pollers.scheduleAtFixedRate(toEmit.emitRunnable, 0, toEmit.period, toEmit.timeUnit);
    }
  }

}
