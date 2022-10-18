/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.lib;

import java.util.Collections;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

class DogStatsDMetricClientTest {

  DogStatsDMetricClient dogStatsDMetricClient;

  @BeforeEach
  void setUp() {
    dogStatsDMetricClient = new DogStatsDMetricClient();
    dogStatsDMetricClient.initialize(MetricEmittingApps.WORKER, new DatadogClientConfiguration("localhost", "1000", false, Collections.emptyList()));
  }

  @AfterEach
  void tearDown() {
    dogStatsDMetricClient.shutdown();
  }

  @Test
  @DisplayName("there should be no exception if we attempt to emit metrics while publish is false")
  void testPublishTrueNoEmitError() {
    Assertions.assertDoesNotThrow(() -> {
      dogStatsDMetricClient.gauge(OssMetricsRegistry.KUBE_POD_PROCESS_CREATE_TIME_MILLISECS, 1);
    });
  }

  @Test
  @DisplayName("there should be no exception if we attempt to emit metrics while publish is true")
  void testPublishFalseNoEmitError() {
    Assertions.assertDoesNotThrow(() -> {
      dogStatsDMetricClient.gauge(OssMetricsRegistry.KUBE_POD_PROCESS_CREATE_TIME_MILLISECS, 1);
    });
  }

  @Test
  @DisplayName("there should be no exception if we attempt to emit metrics without initializing")
  void testNoInitializeNoEmitError() {
    Assertions.assertDoesNotThrow(() -> {
      dogStatsDMetricClient.gauge(OssMetricsRegistry.KUBE_POD_PROCESS_CREATE_TIME_MILLISECS, 1);
    });
  }

}
