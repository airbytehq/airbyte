/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.lib;

/**
 * A mock implementation of MetricClient. Useful for users who do not have any metric client but
 * still want to use the functionality of airbyte.
 */
public class NotImplementedMetricClient implements MetricClient {

  @Override
  public void count(MetricsRegistry metric, double val, String... tags) {
    // Not Implemented.
  }

  @Override
  public void gauge(MetricsRegistry metric, double val, String... tags) {
    // Not Implemented.
  }

  @Override
  public void distribution(MetricsRegistry metric, double val, String... tags) {
    // Not Implemented.
  }

}
