/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.lib;

import lombok.AllArgsConstructor;

/**
 * Enum source of truth of all Airbyte metrics. Each {@link AirbyteMetric} is linked to an
 * application and contains a description to make it easier to understand.
 */
@AllArgsConstructor
public enum AirbyteMetricsRegistry {

  KUBE_POD_PROCESS_CREATE_TIME(
      AirbyteApplications.WORKER,
      new AirbyteMetric("kube_pod_process_create_time", "time taken to create a new kube pod process"));

  public final AirbyteApplication application;
  public final AirbyteMetric metric;

}
