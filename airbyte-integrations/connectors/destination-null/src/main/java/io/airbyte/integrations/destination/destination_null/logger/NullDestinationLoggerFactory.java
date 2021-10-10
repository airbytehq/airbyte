package io.airbyte.integrations.destination.destination_null.logger;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.destination.destination_null.logger.NullDestinationLogger.LoggingType;

public class NullDestinationLoggerFactory {

  private final JsonNode config;

  public NullDestinationLoggerFactory(JsonNode config) {
    this.config = config;
  }

  public NullDestinationLogger create(AirbyteStreamNameNamespacePair streamNamePair) {
    if (!config.has("logging")) {
      throw new IllegalArgumentException("Property logging is required, but not found");
    }

    final JsonNode logConfig = config.get("logging");
    final LoggingType loggingType = LoggingType.valueOf(logConfig.get("logging_type").asText());
    switch (loggingType) {
      case NoLogging -> {
        return DevNull.SINGLETON;
      }
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
