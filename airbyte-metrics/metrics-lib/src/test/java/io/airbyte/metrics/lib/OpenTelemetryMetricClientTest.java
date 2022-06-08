/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.lib;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

class OpenTelemetryMetricClientTest {

  OpenTelemetryMetricClient openTelemetryMetricClient;
  private final static String EXPORTER_ENDPOINT = "http://localhost:4322";

  @BeforeEach
  void setUp() {
    openTelemetryMetricClient = new OpenTelemetryMetricClient();
    openTelemetryMetricClient.initialize(MetricEmittingApps.WORKER, EXPORTER_ENDPOINT);
  }

  @AfterEach
  void tearDown() {
    openTelemetryMetricClient.shutdown();
  }

  @Test
  @DisplayName("there should be no exception if we attempt to emit metrics while publish is false")
  public void testPublishTrueNoEmitError() {
    Assertions.assertDoesNotThrow(() -> {
      openTelemetryMetricClient.gauge(OssMetricsRegistry.KUBE_POD_PROCESS_CREATE_TIME_MILLISECS, 1);
    });
  }

  @Test
  @DisplayName("there should be no exception if we attempt to emit metrics while publish is true")
  public void testPublishFalseNoEmitError() {
    Assertions.assertDoesNotThrow(() -> {
      openTelemetryMetricClient.gauge(OssMetricsRegistry.KUBE_POD_PROCESS_CREATE_TIME_MILLISECS, 1);
    });
  }

  @Test
  @DisplayName("there should be no exception if we attempt to emit metrics without initializing")
  public void testNoInitializeNoEmitError() {
    Assertions.assertDoesNotThrow(() -> {
      openTelemetryMetricClient.gauge(OssMetricsRegistry.KUBE_POD_PROCESS_CREATE_TIME_MILLISECS, 1);
    });
  }

}
