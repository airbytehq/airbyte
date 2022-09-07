/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.lib;

import static io.opentelemetry.api.GlobalOpenTelemetry.resetForTest;
import static io.opentelemetry.api.common.AttributeKey.stringKey;
import static io.opentelemetry.semconv.resource.attributes.ResourceAttributes.SERVICE_NAME;

import com.google.common.annotations.VisibleForTesting;
import io.opentelemetry.api.OpenTelemetry;
import io.opentelemetry.api.common.Attributes;
import io.opentelemetry.api.common.AttributesBuilder;
import io.opentelemetry.api.metrics.DoubleHistogram;
import io.opentelemetry.api.metrics.LongCounter;
import io.opentelemetry.api.metrics.Meter;
import io.opentelemetry.api.trace.propagation.W3CTraceContextPropagator;
import io.opentelemetry.context.propagation.ContextPropagators;
import io.opentelemetry.exporter.otlp.metrics.OtlpGrpcMetricExporter;
import io.opentelemetry.exporter.otlp.trace.OtlpGrpcSpanExporter;
import io.opentelemetry.sdk.OpenTelemetrySdk;
import io.opentelemetry.sdk.metrics.SdkMeterProvider;
import io.opentelemetry.sdk.metrics.export.MetricExporter;
import io.opentelemetry.sdk.metrics.export.PeriodicMetricReader;
import io.opentelemetry.sdk.resources.Resource;
import io.opentelemetry.sdk.trace.SdkTracerProvider;
import io.opentelemetry.sdk.trace.export.BatchSpanProcessor;

/**
 * Implementation of the {@link MetricClient} that sends the provided metric data to an
 * OpenTelemetry compliant metrics store.
 * <p>
 * Any {@link MetricAttribute}s provided along with the metric data are passed as key/value pairs
 * annotating the metric.
 */
public class OpenTelemetryMetricClient implements MetricClient {

  private Meter meter;
  private SdkMeterProvider meterProvider;

  @Override
  public void count(final MetricsRegistry metric, final long val, final MetricAttribute... attributes) {
    final LongCounter counter = meter
        .counterBuilder(metric.getMetricName())
        .setDescription(metric.getMetricDescription())
        .build();

    final AttributesBuilder attributesBuilder = buildAttributes(attributes);
    counter.add(val, attributesBuilder.build());
  }

  @Override
  public void gauge(final MetricsRegistry metric, final double val, final MetricAttribute... attributes) {
    final AttributesBuilder attributesBuilder = buildAttributes(attributes);
    meter.gaugeBuilder(metric.getMetricName()).setDescription(metric.getMetricDescription())
        .buildWithCallback(measurement -> measurement.record(val, attributesBuilder.build()));
  }

  @Override
  public void distribution(final MetricsRegistry metric, final double val, final MetricAttribute... attributes) {
    final DoubleHistogram histogramMeter = meter.histogramBuilder(metric.getMetricName()).setDescription(metric.getMetricDescription()).build();
    final AttributesBuilder attributesBuilder = buildAttributes(attributes);
    histogramMeter.record(val, attributesBuilder.build());
  }

  public void initialize(final MetricEmittingApp metricEmittingApp, final String otelEndpoint) {
    final Resource resource = Resource.getDefault().toBuilder().put(SERVICE_NAME, metricEmittingApp.getApplicationName()).build();

    final SdkTracerProvider sdkTracerProvider = SdkTracerProvider.builder()
        .addSpanProcessor(
            BatchSpanProcessor
                .builder(OtlpGrpcSpanExporter.builder().setEndpoint(otelEndpoint).build())
                .build())
        .setResource(resource)
        .build();
    final MetricExporter metricExporter = OtlpGrpcMetricExporter.builder()
        .setEndpoint(otelEndpoint).build();
    initialize(metricEmittingApp, metricExporter, sdkTracerProvider, resource);
  }

  @VisibleForTesting
  SdkMeterProvider getSdkMeterProvider() {
    return meterProvider;
  }

  @VisibleForTesting
  void initialize(
                  final MetricEmittingApp metricEmittingApp,
                  final MetricExporter metricExporter,
                  final SdkTracerProvider sdkTracerProvider,
                  final Resource resource) {
    meterProvider = SdkMeterProvider.builder()
        .registerMetricReader(PeriodicMetricReader.builder(metricExporter).build())
        .setResource(resource)
        .build();

    final OpenTelemetry openTelemetry = OpenTelemetrySdk.builder()
        .setTracerProvider(sdkTracerProvider)
        .setMeterProvider(meterProvider)
        .setPropagators(ContextPropagators.create(W3CTraceContextPropagator.getInstance()))
        .buildAndRegisterGlobal();

    meter = openTelemetry.meterBuilder(metricEmittingApp.getApplicationName())
        .build();
  }

  @Override
  public void shutdown() {
    resetForTest();
  }

  private AttributesBuilder buildAttributes(final MetricAttribute... attributes) {
    final AttributesBuilder attributesBuilder = Attributes.builder();
    for (final MetricAttribute attribute : attributes) {
      attributesBuilder.put(stringKey(attribute.key()), attribute.value());
    }
    return attributesBuilder;
  }

}
