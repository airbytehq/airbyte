/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.lib;

import static io.opentelemetry.api.GlobalOpenTelemetry.resetForTest;
import static io.opentelemetry.api.common.AttributeKey.stringKey;
import static io.opentelemetry.semconv.resource.attributes.ResourceAttributes.SERVICE_NAME;

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
import io.opentelemetry.sdk.metrics.export.PeriodicMetricReader;
import io.opentelemetry.sdk.resources.Resource;
import io.opentelemetry.sdk.trace.SdkTracerProvider;
import io.opentelemetry.sdk.trace.export.BatchSpanProcessor;

public class OpenTelemetryMetricClient implements MetricClient {

  private Meter meter;

  @Override
  public void count(MetricsRegistry metric, long val, String... tags) {
    LongCounter counter = meter
        .counterBuilder(metric.getMetricName())
        .setDescription(metric.getMetricDescription())
        .build();

    AttributesBuilder attributesBuilder = Attributes.builder();
    for (String tag : tags) {
      attributesBuilder.put(stringKey(tag), tag);
    }

    counter.add(val, attributesBuilder.build());
  }

  @Override
  public void gauge(MetricsRegistry metric, double val, String... tags) {
    AttributesBuilder attributesBuilder = Attributes.builder();
    for (String tag : tags) {
      attributesBuilder.put(stringKey(tag), tag);
    }
    meter.gaugeBuilder(metric.getMetricName()).setDescription(metric.getMetricDescription())
        .buildWithCallback(measurement -> measurement.record(val, attributesBuilder.build()));
  }

  @Override
  public void distribution(MetricsRegistry metric, double val, String... tags) {
    DoubleHistogram histogramMeter = meter.histogramBuilder(metric.getMetricName()).setDescription(metric.getMetricDescription()).build();
    AttributesBuilder attributesBuilder = Attributes.builder();

    for (String tag : tags) {
      attributesBuilder.put(stringKey(tag), tag);
    }
    histogramMeter.record(val, attributesBuilder.build());
  }

  public void initialize(MetricEmittingApp metricEmittingApp, String otelEndpoint) {
    Resource resource = Resource.getDefault().toBuilder().put(SERVICE_NAME, metricEmittingApp.getApplicationName()).build();

    SdkTracerProvider sdkTracerProvider = SdkTracerProvider.builder()
        .addSpanProcessor(
            BatchSpanProcessor
                .builder(OtlpGrpcSpanExporter.builder().setEndpoint(otelEndpoint).build())
                .build())
        .setResource(resource)
        .build();
    OtlpGrpcMetricExporter metricExporter = OtlpGrpcMetricExporter.builder()
        .setEndpoint(otelEndpoint).build();
    SdkMeterProvider meterProvider = SdkMeterProvider.builder()
        .registerMetricReader(PeriodicMetricReader.builder(metricExporter).build())
        .setResource(resource)
        .build();

    OpenTelemetry openTelemetry = OpenTelemetrySdk.builder()
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

}
