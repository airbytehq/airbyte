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
  public static MetricClient getMetricClient() {
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
    initializeDatadogStatsDMetricClient(metricEmittingApp);
  }

  private static DogStatsDMetricClient initializeDatadogStatsDMetricClient(
                                                                           MetricEmittingApp metricEmittingApp) {
    DogStatsDMetricClient client = new DogStatsDMetricClient();
    final Configs configs = new EnvConfigs();

    client.initialize(metricEmittingApp, new DatadogClientConfiguration(configs));
    metricClient = client;
    return client;
  }

  static void flush() {
    if (metricClient != null) {
      metricClient.shutdown();
    }
    metricClient = null;
  }

}
