/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.e2e_test;

import com.fasterxml.jackson.databind.JsonNode;
import datadog.trace.api.Trace;
import io.airbyte.cdk.integrations.BaseConnector;
import io.airbyte.cdk.integrations.base.Source;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.opentracing.Scope;
import io.opentracing.Span;
import io.opentracing.util.GlobalTracer;

/**
 * This source is optimized for creating records very fast. It optimizes for speed over flexibility.
 */
public class SpeedBenchmarkSource extends BaseConnector implements Source {

  @Override
  public AirbyteConnectionStatus check(final JsonNode jsonConfig) {
    try {
      final SpeedBenchmarkConfig sourceConfig = SpeedBenchmarkConfig.parseFromConfig(jsonConfig);
      return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED).withMessage("Source config: " + sourceConfig);
    } catch (final Exception e) {
      return new AirbyteConnectionStatus().withStatus(Status.FAILED).withMessage(e.getMessage());
    }
  }

  @Override
  public AirbyteCatalog discover(final JsonNode jsonConfig) throws Exception {
    final SpeedBenchmarkConfig sourceConfig = SpeedBenchmarkConfig.parseFromConfig(jsonConfig);
    return sourceConfig.getCatalog();
  }

  @Override
  @SuppressWarnings("try")
  public AutoCloseableIterator<AirbyteMessage> read(final JsonNode jsonConfig, final ConfiguredAirbyteCatalog catalog, final JsonNode state) {
    final Span span = GlobalTracer.get().buildSpan("read").asChildOf(GlobalTracer.get().activeSpan()).start();
    try (final Scope ignored = GlobalTracer.get().activateSpan(span)) {
      final SpeedBenchmarkConfig sourceConfig = SpeedBenchmarkConfig.parseFromConfig(jsonConfig);
      return AutoCloseableIterators.fromIterator(new SpeedBenchmarkGeneratorIterator(sourceConfig.maxRecords()));
    }
  }

}
