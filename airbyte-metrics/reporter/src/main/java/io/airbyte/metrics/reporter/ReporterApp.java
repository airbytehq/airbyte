package io.airbyte.metrics.reporter;

import io.airbyte.metrics.lib.DogstatsdMetricSingleton;

public class ReporterApp {

  public static void main(final String[] args) {
    DogstatsdMetricSingleton.initialize("airbyte-metrics-reporter", false);
  }

}
