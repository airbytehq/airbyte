/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.e2e_test;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.BaseConnector;
import io.airbyte.cdk.integrations.base.Source;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;

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
  public AutoCloseableIterator<AirbyteMessage> read(final JsonNode jsonConfig, final ConfiguredAirbyteCatalog catalog, final JsonNode state)
      throws Exception {
    final SpeedBenchmarkConfig sourceConfig = SpeedBenchmarkConfig.parseFromConfig(jsonConfig);
    return AutoCloseableIterators.fromIterator(new SpeedBenchmarkGeneratorIterator(sourceConfig.maxRecords()));
  }

}
