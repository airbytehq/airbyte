/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.lib;

import static io.airbyte.metrics.lib.MetricClientFactory.DATADOG_METRIC_CLIENT;

import io.airbyte.config.Configs;
import io.airbyte.config.EnvConfigs;
import io.micrometer.core.instrument.Clock;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.statsd.StatsdConfig;
import io.micrometer.statsd.StatsdMeterRegistry;

public class MicroMeterRegistryFactory {

  private static final Configs configs = new EnvConfigs();

  private static StatsdConfig getDatadogStatsDConfig() {
    return new StatsdConfig() {

      /**
       * @return
       */
      @Override
      public String host() {
        return configs.getDDAgentHost();
      }

      /**
       * @param key Key to lookup in the config.
       * @return
       */
      @Override
      public String get(String key) {
        return null;
      }

    };
  }

  public static MeterRegistry getMeterRegistry() {

    if (configs.getMetricClient().equals(DATADOG_METRIC_CLIENT)) {
      StatsdConfig config = getDatadogStatsDConfig();
      return new StatsdMeterRegistry(config, Clock.SYSTEM);
    }

    // We do not support open telemetry yet.
    return null;
  }

}
