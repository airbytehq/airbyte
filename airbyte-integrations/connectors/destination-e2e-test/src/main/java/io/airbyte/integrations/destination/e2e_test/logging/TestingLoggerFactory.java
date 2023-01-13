/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.e2e_test.logging;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.e2e_test.logging.TestingLogger.LoggingType;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;

public class TestingLoggerFactory {

  private final JsonNode config;

  public TestingLoggerFactory(final JsonNode config) {
    this.config = config;
  }

  public TestingLogger create(final AirbyteStreamNameNamespacePair streamNamePair) {
    if (!config.has("logging_config")) {
      throw new IllegalArgumentException("Property logging_config is required, but not found");
    }

    final JsonNode logConfig = config.get("logging_config");
    final LoggingType loggingType = LoggingType.valueOf(logConfig.get("logging_type").asText());
    switch (loggingType) {
      case FirstN -> {
        final int maxEntryCount = logConfig.get("max_entry_count").asInt();
        return new FirstNLogger(streamNamePair, maxEntryCount);
      }
      case EveryNth -> {
        final int nthEntryToLog = logConfig.get("nth_entry_to_log").asInt();
        final int maxEntryCount = logConfig.get("max_entry_count").asInt();
        return new EveryNthLogger(streamNamePair, nthEntryToLog, maxEntryCount);
      }
      case RandomSampling -> {
        final double samplingRatio = logConfig.get("sampling_ratio").asDouble();
        final long seed = logConfig.has("seed") ? logConfig.get("seed").asLong() : System.currentTimeMillis();
        final int maxEntryCount = logConfig.get("max_entry_count").asInt();
        return new RandomSamplingLogger(streamNamePair, samplingRatio, seed, maxEntryCount);
      }
      default -> throw new IllegalArgumentException("Unexpected logging type: " + loggingType);
    }
  }

}
