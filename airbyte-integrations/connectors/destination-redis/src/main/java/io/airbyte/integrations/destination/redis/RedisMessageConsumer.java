/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redis;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.time.Instant;
import java.util.Map;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

class RedisMessageConsumer extends FailureTrackingAirbyteMessageConsumer {

  private static final Logger LOGGER = LoggerFactory.getLogger(RedisMessageConsumer.class);

  private final Consumer<AirbyteMessage> outputRecordCollector;

  private final ConfiguredAirbyteCatalog configuredCatalog;

  private Map<AirbyteStreamNameNamespacePair, RedisStreamConfig> redisStreams;

  private final RedisNameTransformer nameTransformer;

  private final RedisCache redisCache;

  private AirbyteMessage lastMessage = null;

  public RedisMessageConsumer(JsonNode redisConfig,
                              ConfiguredAirbyteCatalog configuredCatalog,
                              Consumer<AirbyteMessage> outputRecordCollector) {
    this.configuredCatalog = configuredCatalog;
    this.outputRecordCollector = outputRecordCollector;
    this.redisCache = RedisCacheFactory.newInstance(redisConfig);
    this.nameTransformer = new RedisNameTransformer();
  }

  @Override
  protected void startTracked() {
    this.redisStreams = configuredCatalog.getStreams().stream()
        .collect(Collectors.toUnmodifiableMap(
            AirbyteStreamNameNamespacePair::fromConfiguredAirbyteSteam,
            k -> new RedisStreamConfig(
                nameTransformer.keyName(k.getStream().getNamespace(), k.getStream().getName()),
                nameTransformer.tmpKeyName(k.getStream().getNamespace(), k.getStream().getName()),
                k.getDestinationSyncMode())));
  }

  @Override
  protected void acceptTracked(AirbyteMessage message) {
    if (message.getType() == AirbyteMessage.Type.RECORD) {
      var messageRecord = message.getRecord();
      var streamConfig =
          redisStreams.get(AirbyteStreamNameNamespacePair.fromRecordMessage(messageRecord));
      if (streamConfig == null) {
        throw new IllegalArgumentException("Unrecognized destination stream");
      }

      var timestamp = Instant.ofEpochMilli(messageRecord.getEmittedAt());
      redisCache.insert(streamConfig.getTmpKey(), timestamp, Jsons.serialize(messageRecord.getData()));
    } else if (message.getType() == AirbyteMessage.Type.STATE) {
      this.lastMessage = message;
    } else {
      LOGGER.warn("Unsupported airbyte message type: {}", message.getType());
    }
  }

  @Override
  protected void close(boolean hasFailed) {
    if (!hasFailed) {
      redisStreams.forEach((k, v) -> {
        try {
          switch (v.getDestinationSyncMode()) {
            case APPEND -> redisCache.copy(v.getTmpKey(), v.getKey(), false);
            case OVERWRITE -> redisCache.copy(v.getTmpKey(), v.getKey(), true);
            default -> throw new UnsupportedOperationException("Unsupported destination sync mode");
          }
        } catch (Exception e) {
          LOGGER.error("Error while synchronizing keys: ", e);
        }
      });
      outputRecordCollector.accept(lastMessage);
    }

    try {
      redisStreams.forEach((k, v) -> redisCache.delete(v.getTmpKey()));
    } catch (Exception e) {
      LOGGER.error("Error while deleting tmp keys: ", e);
    }

    redisCache.close();

  }

}
