/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.reporter;

import io.airbyte.config.Configs;
import io.airbyte.config.EnvConfigs;
import io.airbyte.metrics.lib.DatadogClientConfiguration;
import io.airbyte.metrics.lib.DogStatsDMetricSingleton;
import io.airbyte.metrics.lib.MetricEmittingApps;

public class ReporterApp {

  public static void main(final String[] args) {
    final Configs configs = new EnvConfigs();
    DogStatsDMetricSingleton.initialize(MetricEmittingApps.METRICS_REPORTER, new DatadogClientConfiguration(configs));
  }

}
