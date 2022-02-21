/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.reporter;

import io.airbyte.metrics.lib.AirbyteApplications;
import io.airbyte.metrics.lib.DogStatsDMetricSingleton;

public class ReporterApp {

  public static void main(final String[] args) {
    DogStatsDMetricSingleton.initialize(AirbyteApplications.METRICS_REPORTER, false);
  }

}
