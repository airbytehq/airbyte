/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.lib;

import io.airbyte.config.Configs;
import io.airbyte.config.EnvConfigs;
import io.micrometer.core.instrument.Clock;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.statsd.StatsdConfig;
import io.micrometer.statsd.StatsdMeterRegistry;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * A singleton factory producing a singleton metric client.
 */
public class MetricClientFactory {

  private static final Logger LOGGER = LoggerFactory.getLogger(MetricClientFactory.class);

  static final String DATADOG_METRIC_CLIENT = "datadog";
  private static final String OTEL_METRIC_CLIENT = "otel";

  private static final Configs configs = new EnvConfigs();

  private MetricClientFactory() {
    // no explicit implementation
  }

  private static MetricClient metricClient;

  /**
   *
   * Retrieve previously created metric client. If metric client was not created before, returns a
   * NotImplementedMetricClient instead.
   *
   * @return previously created metric client which has been properly initialized, or an instance of
   *         the empty NotImplementedMetricClient.
   */
  public synchronized static MetricClient getMetricClient() {
    if (metricClient != null) {
      return metricClient;
    }
    LOGGER.warn(
        "MetricClient has not been initialized. Must call MetricClientFactory.CreateMetricClient before using MetricClient. Using a dummy client for now. Ignore this if Airbyte is configured to not publish any metrics.");

    return new NotImplementedMetricClient();
  }

  /**
   *
   * Create and initialize a MetricClient based on System env.
   *
   * @param metricEmittingApp the name of the app which the metric will be running under.
   */
  public static synchronized void initialize(final MetricEmittingApp metricEmittingApp) {
    if (metricClient != null) {
      LOGGER.warn("Metric client is already initialized to " + configs.getMetricClient());
      return;
    }

    if (DATADOG_METRIC_CLIENT.equals(configs.getMetricClient())) {
      if (configs.getDDAgentHost() == null || configs.getDDDogStatsDPort() == null) {
        throw new RuntimeException("DD_AGENT_HOST is null or DD_DOGSTATSD_PORT is null. Both are required to use the DataDog Metric Client");
      } else {
        initializeDatadogMetricClient(metricEmittingApp);
      }
    } else if (OTEL_METRIC_CLIENT.equals(configs.getMetricClient())) {
      initializeOpenTelemetryMetricClient(metricEmittingApp);
    } else {
      metricClient = new NotImplementedMetricClient();
      LOGGER.warn(
          "MetricClient was not recognized or not provided. Accepted values are `datadog` or `otel`. ");
    }
  }

  /**
   * A statsd config for micrometer. We override host to be the datadog agent address, while keeping
   * other settings default.
   */
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
       * Returning null for default get function because the host has been overridden above.
       */
      @Override
      public String get(final String key) {
        return null;
      }

    };
  }

  /**
   *
   * Returns a meter registry to be consumed by temporal configs.
   *
   */
  public static MeterRegistry getMeterRegistry() {

    if (DATADOG_METRIC_CLIENT.equals(configs.getMetricClient())) {
      final StatsdConfig config = getDatadogStatsDConfig();
      return new StatsdMeterRegistry(config, Clock.SYSTEM);
    }

    // To support open telemetry, we need to use a different type of Config. For now we simply return
    // null - in this case, we do not register any metric emitting mechanism in temporal and thus
    // users will not receive temporal related metrics.
    return null;
  }

  private static DogStatsDMetricClient initializeDatadogMetricClient(
                                                                     final MetricEmittingApp metricEmittingApp) {
    final DogStatsDMetricClient client = new DogStatsDMetricClient();

    client.initialize(metricEmittingApp, new DatadogClientConfiguration(configs));
    metricClient = client;
    return client;
  }

  private static OpenTelemetryMetricClient initializeOpenTelemetryMetricClient(
                                                                               final MetricEmittingApp metricEmittingApp) {
    final OpenTelemetryMetricClient client = new OpenTelemetryMetricClient();
    client.initialize(metricEmittingApp, configs.getOtelCollectorEndpoint());
    metricClient = client;
    return client;
  }

  synchronized static void flush() {
    if (metricClient != null) {
      metricClient.shutdown();
      metricClient = null;
    }
  }

}
