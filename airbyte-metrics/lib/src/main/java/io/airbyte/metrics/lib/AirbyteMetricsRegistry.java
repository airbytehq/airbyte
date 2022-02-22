/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.lib;

import com.google.api.client.util.Preconditions;

/**
 * Enum source of truth of all Airbyte metrics. Each enum value represent a metric and is linked to
 * an application and contains a description to make it easier to understand.
 *
 * Each object of the enum actually represent a metric, so the Registry name is misleading. The
 * reason 'Registry' is in the name is to emphasize this enum's purpose as a source of truth for all
 * metrics. This also helps code readability i.e. AirbyteMetricsRegistry.metricA.
 *
 * Metric Name Convention (adapted from
 * https://docs.datadoghq.com/developers/guide/what-best-practices-are-recommended-for-naming-metrics-and-tags/):
 * <p>
 * - Use lowercase. Metric names are case sensitive.
 * <p>
 * - Use underscore to delimit names with multiple words.
 * <p>
 * - No spaces. This makes the metric confusing to read.
 * <p>
 * - Avoid numbers. This makes the metric confusing to read. Numbers should only be used as a
 * <p>
 * - Add units at name end if applicable. This is especially relevant for time units. versioning
 * tactic and present at the end of the metric.
 */
public enum AirbyteMetricsRegistry {

  KUBE_POD_PROCESS_CREATE_TIME_MILLISECS(
      MetricEmittingApps.WORKER,
      "kube_pod_process_create_time_millisecs",
      "time taken to create a new kube pod process");

  public final MetricEmittingApp application;
  public final String metricName;
  public final String metricDescription;

  AirbyteMetricsRegistry(final MetricEmittingApp application, final String metricName, final String metricDescription) {
    Preconditions.checkNotNull(metricDescription);
    Preconditions.checkNotNull(application);

    this.application = application;
    this.metricName = metricName;
    this.metricDescription = metricDescription;
  }

}
