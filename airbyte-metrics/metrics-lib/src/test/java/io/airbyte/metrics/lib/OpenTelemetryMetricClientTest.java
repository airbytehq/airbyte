/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.lib;

import static io.opentelemetry.semconv.resource.attributes.ResourceAttributes.SERVICE_NAME;
import static org.assertj.core.api.AssertionsForClassTypes.assertThat;

import com.google.common.collect.Iterables;
import io.opentelemetry.api.common.AttributeKey;
import io.opentelemetry.sdk.metrics.SdkMeterProvider;
import io.opentelemetry.sdk.metrics.data.MetricData;
import io.opentelemetry.sdk.resources.Resource;
import io.opentelemetry.sdk.testing.exporter.InMemoryMetricExporter;
import io.opentelemetry.sdk.trace.SdkTracerProvider;
import java.util.List;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

class OpenTelemetryMetricClientTest {

  OpenTelemetryMetricClient openTelemetryMetricClient;
  private final static String TAG = "tag1";

  private final static MetricEmittingApp METRIC_EMITTING_APP = MetricEmittingApps.WORKER;
  private InMemoryMetricExporter metricExporter;
  private SdkMeterProvider metricProvider;

  @BeforeEach
  void setUp() {
    openTelemetryMetricClient = new OpenTelemetryMetricClient();

    final Resource resource = Resource.getDefault().toBuilder().put(SERVICE_NAME, METRIC_EMITTING_APP.getApplicationName()).build();
    metricExporter = InMemoryMetricExporter.create();
    final SdkTracerProvider sdkTracerProvider = SdkTracerProvider.builder()
        .setResource(resource)
        .build();
    openTelemetryMetricClient.initialize(METRIC_EMITTING_APP, metricExporter, sdkTracerProvider, resource);

    metricProvider = openTelemetryMetricClient.getSdkMeterProvider();
  }

  @AfterEach
  void tearDown() {
    openTelemetryMetricClient.shutdown();
  }

  @Test
  @DisplayName("Should send out count metric with correct metric name, description and value")
  void testCountSuccess() {
    openTelemetryMetricClient.count(OssMetricsRegistry.KUBE_POD_PROCESS_CREATE_TIME_MILLISECS, 1);

    metricProvider.forceFlush();
    final List<MetricData> metricDataList = metricExporter.getFinishedMetricItems();
    final MetricData data = Iterables.getOnlyElement(metricDataList);

    assertThat(data.getName()).isEqualTo(OssMetricsRegistry.KUBE_POD_PROCESS_CREATE_TIME_MILLISECS.getMetricName());
    assertThat(data.getDescription()).isEqualTo(OssMetricsRegistry.KUBE_POD_PROCESS_CREATE_TIME_MILLISECS.getMetricDescription());
    assertThat(data.getLongSumData().getPoints().stream().anyMatch(longPointData -> longPointData.getValue() == 1L));
  }

  @Test
  @DisplayName("Tags should be passed into metrics")
  void testCountWithTagSuccess() {
    openTelemetryMetricClient.count(OssMetricsRegistry.KUBE_POD_PROCESS_CREATE_TIME_MILLISECS, 1, new MetricAttribute(TAG, TAG));

    metricProvider.forceFlush();
    final List<MetricData> metricDataList = metricExporter.getFinishedMetricItems();
    final MetricData data = Iterables.getOnlyElement(metricDataList);

    assertThat(data.getName()).isEqualTo(OssMetricsRegistry.KUBE_POD_PROCESS_CREATE_TIME_MILLISECS.getMetricName());
    assertThat(data.getDescription()).isEqualTo(OssMetricsRegistry.KUBE_POD_PROCESS_CREATE_TIME_MILLISECS.getMetricDescription());
    assertThat(data.getLongSumData().getPoints().stream()
        .anyMatch(
            longPointData -> longPointData.getValue() == 1L && TAG.equals(longPointData.getAttributes().get(AttributeKey.stringKey(TAG)))));
  }

  @Test
  @DisplayName("Should send out gauge metric with correct metric name, description and value")
  void testGaugeSuccess() throws Exception {
    openTelemetryMetricClient.gauge(OssMetricsRegistry.KUBE_POD_PROCESS_CREATE_TIME_MILLISECS, 1);

    metricProvider.forceFlush();
    final List<MetricData> metricDataList = metricExporter.getFinishedMetricItems();
    final MetricData data = Iterables.getOnlyElement(metricDataList);

    assertThat(data.getName()).isEqualTo(OssMetricsRegistry.KUBE_POD_PROCESS_CREATE_TIME_MILLISECS.getMetricName());
    assertThat(data.getDescription()).isEqualTo(OssMetricsRegistry.KUBE_POD_PROCESS_CREATE_TIME_MILLISECS.getMetricDescription());
    assertThat(data.getDoubleGaugeData().getPoints().stream().anyMatch(doublePointData -> doublePointData.getValue() == 1.0));
  }

  @Test
  @DisplayName("Should send out histogram metric with correct metric name, description and value")
  void testHistogramSuccess() {
    openTelemetryMetricClient.distribution(OssMetricsRegistry.KUBE_POD_PROCESS_CREATE_TIME_MILLISECS, 10);
    openTelemetryMetricClient.distribution(OssMetricsRegistry.KUBE_POD_PROCESS_CREATE_TIME_MILLISECS, 30);

    metricProvider.forceFlush();
    final List<MetricData> metricDataList = metricExporter.getFinishedMetricItems();
    final MetricData data = Iterables.getOnlyElement(metricDataList);

    assertThat(data.getName()).isEqualTo(OssMetricsRegistry.KUBE_POD_PROCESS_CREATE_TIME_MILLISECS.getMetricName());
    assertThat(data.getDescription()).isEqualTo(OssMetricsRegistry.KUBE_POD_PROCESS_CREATE_TIME_MILLISECS.getMetricDescription());
    assertThat(data.getHistogramData().getPoints().stream().anyMatch(histogramPointData -> histogramPointData.getMax() == 30.0));
    assertThat(data.getHistogramData().getPoints().stream().anyMatch(histogramPointData -> histogramPointData.getMin() == 10.0));
  }

}
