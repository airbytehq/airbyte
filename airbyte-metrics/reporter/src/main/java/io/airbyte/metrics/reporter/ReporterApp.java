/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.reporter;

import io.airbyte.metrics.lib.DogStatsDMetricSingleton;
import io.airbyte.metrics.lib.MetricEmittingApps;

public class ReporterApp {

  public static void main(final String[] args) {
    DogStatsDMetricSingleton.initialize(MetricEmittingApps.METRICS_REPORTER, false);
  }

}
