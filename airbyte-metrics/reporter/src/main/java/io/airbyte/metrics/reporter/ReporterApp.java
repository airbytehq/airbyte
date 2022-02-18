/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.reporter;

import io.airbyte.metrics.lib.DogstatsdMetricSingleton;

public class ReporterApp {

  public static void main(final String[] args) {
    DogstatsdMetricSingleton.initialize("airbyte-metrics-reporter", false);
  }

}
