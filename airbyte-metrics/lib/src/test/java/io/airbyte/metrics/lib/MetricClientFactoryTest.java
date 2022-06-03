/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.lib;

import static org.hamcrest.CoreMatchers.instanceOf;
import static org.hamcrest.MatcherAssert.assertThat;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

public class MetricClientFactoryTest {

  @AfterEach
  void tearDown() {
    MetricClientFactory.flush();
  }

  @Test
  @DisplayName("Should not throw error if calling get without calling create;")
  public void testMetricClientFactoryGetMetricOnlyDoNotThrow() {
    MetricClient metricClient = MetricClientFactory.getMetricClient();
    assertThat(metricClient, instanceOf(NotImplementedMetricClient.class));
  }

  @Test
  @DisplayName("Should not throw error if MetricClientFactory creates a metric client on the first call;")
  public void testMetricClientFactoryCreateSuccess() {
    Assertions.assertDoesNotThrow(() -> {
      MetricClientFactory.initialize(MetricEmittingApps.METRICS_REPORTER);
    });
  }

  @Test
  @DisplayName("Should throw error if MetricClientFactory create a metric client multiple times;")
  public void testMetricClientFactoryCreateMultipleTimesThrows() {
    Assertions.assertThrows(RuntimeException.class, () -> {
      MetricClientFactory.initialize(MetricEmittingApps.METRICS_REPORTER);
      MetricClientFactory.initialize(MetricEmittingApps.METRICS_REPORTER);
    });
  }

}
