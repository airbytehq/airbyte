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
 * reason 'Registry' in the name is to emphasize this enum's purpose as a source of truth for all
 * metrics. This also helps code readability i.e. AirbyteMetricsRegistry.metricA.
 *
 */
public enum AirbyteMetricsRegistry {

  KUBE_POD_PROCESS_CREATE_TIME(AirbyteApplications.WORKER,
      "kube_pod_process_create_time", "time taken to create a new kube pod process");

  public final AirbyteApplication application;
  public final String metricName;
  public final String metricDescription;

  AirbyteMetricsRegistry(final AirbyteApplication application, final String metricName, final String metricDescription) {
    Preconditions.checkNotNull(metricDescription);
    Preconditions.checkNotNull(application);

    this.application = application;
    this.metricName = metricName;
    this.metricDescription = metricDescription;
  }

}
