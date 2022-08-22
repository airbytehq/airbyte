/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.lib;

import java.util.Collections;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

class DogStatsDMetricSingletonTest {

  @AfterEach
  void tearDown() {
    DogStatsDMetricSingleton.flush();
  }

  @Test
  @DisplayName("there should be no exception if we attempt to emit metrics while publish is false")
  void testPublishTrueNoEmitError() {
    Assertions.assertDoesNotThrow(() -> {
      DogStatsDMetricSingleton.initialize(MetricEmittingApps.WORKER,
          new DatadogClientConfiguration("localhost", "1000", false, Collections.emptyList()));
      DogStatsDMetricSingleton.gauge(OssMetricsRegistry.KUBE_POD_PROCESS_CREATE_TIME_MILLISECS, 1);
    });
  }

  @Test
  @DisplayName("there should be no exception if we attempt to emit metrics while publish is true")
  void testPublishFalseNoEmitError() {
    Assertions.assertDoesNotThrow(() -> {
      DogStatsDMetricSingleton.initialize(MetricEmittingApps.WORKER,
          new DatadogClientConfiguration("localhost", "1000", true, Collections.emptyList()));
      DogStatsDMetricSingleton.gauge(OssMetricsRegistry.KUBE_POD_PROCESS_CREATE_TIME_MILLISECS, 1);
    });
  }

  @Test
  @DisplayName("there should be no exception if we attempt to emit metrics without initializing")
  void testNoInitializeNoEmitError() {
    Assertions.assertDoesNotThrow(() -> {
      DogStatsDMetricSingleton.gauge(OssMetricsRegistry.KUBE_POD_PROCESS_CREATE_TIME_MILLISECS, 1);
    });
  }

}
