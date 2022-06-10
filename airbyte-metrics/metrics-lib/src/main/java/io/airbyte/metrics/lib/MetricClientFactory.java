/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.lib;

import io.airbyte.config.Configs;
import io.airbyte.config.EnvConfigs;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * A singleton factory producing a singleton metric client.
 */
public class MetricClientFactory {

  private static final Logger LOGGER = LoggerFactory.getLogger(MetricClientFactory.class);

  private static final String DATADOG_METRIC_CLIENT = "datadog";
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
  public static synchronized void initialize(MetricEmittingApp metricEmittingApp) {
    if (metricClient != null) {
      throw new RuntimeException("You cannot initialize configuration more than once.");
    }

    if (configs.getMetricClient().equals(DATADOG_METRIC_CLIENT)) {
      initializeDatadogMetricClient(metricEmittingApp);
    } else if (configs.getMetricClient().equals(OTEL_METRIC_CLIENT)) {
      initializeOpenTelemetryMetricClient(metricEmittingApp);
    } else {
      metricClient = new NotImplementedMetricClient();
      LOGGER.warn(
          "MetricClient was not recognized or not provided. Accepted values are `datadog` or `otel`. ");
    }
  }

  private static DogStatsDMetricClient initializeDatadogMetricClient(
                                                                     MetricEmittingApp metricEmittingApp) {
    DogStatsDMetricClient client = new DogStatsDMetricClient();

    client.initialize(metricEmittingApp, new DatadogClientConfiguration(configs));
    metricClient = client;
    return client;
  }

  private static OpenTelemetryMetricClient initializeOpenTelemetryMetricClient(
                                                                               MetricEmittingApp metricEmittingApp) {
    OpenTelemetryMetricClient client = new OpenTelemetryMetricClient();
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
