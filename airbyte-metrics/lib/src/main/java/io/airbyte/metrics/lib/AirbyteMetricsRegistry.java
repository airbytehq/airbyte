/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.lib;

import lombok.AllArgsConstructor;

@AllArgsConstructor
public enum AirbyteMetricsRegistry {

  KUBE_POD_PROCESS_CREATE_TIME(AirbyteApplications.AIRBYTE_SCHEDULER, "kube_pod_process_create_time", "time taken to create a new kube pod process");

  private final AirbyteApplication application;
  private final String metricName;
  private final String metricDescription;

}
