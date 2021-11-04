/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redis;

import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
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

  private final RedisOpsProvider redisOpsProvider;

  private AirbyteMessage lastMessage = null;

  public RedisMessageConsumer(RedisConfig redisConfig,
                              ConfiguredAirbyteCatalog configuredCatalog,
                              Consumer<AirbyteMessage> outputRecordCollector) {
    this.configuredCatalog = configuredCatalog;
    this.outputRecordCollector = outputRecordCollector;
    this.redisOpsProvider = new RedisOpsProvider(redisConfig);
    this.nameTransformer = new RedisNameTransformer();
  }

  @Override
  protected void startTracked() throws Exception {
    this.redisStreams = configuredCatalog.getStreams().stream()
        .collect(Collectors.toUnmodifiableMap(
            AirbyteStreamNameNamespacePair::fromConfiguredAirbyteSteam,
            k -> new RedisStreamConfig(
                nameTransformer.outputNamespace(k.getStream().getNamespace()),
                nameTransformer.outputKey(k.getStream().getName()),
                nameTransformer.outputTmpKey(k.getStream().getName()),
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
      var data = Jsons.serialize(messageRecord.getData());
      redisOpsProvider.insert(streamConfig.getNamespace(), streamConfig.getTmpKeyName(), data);
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
            case APPEND -> {
              redisOpsProvider.rename(v.getNamespace(), v.getTmpKeyName(), v.getKeyName());
            }
            case OVERWRITE -> {
              redisOpsProvider.delete(v.getNamespace(), v.getKeyName());
              redisOpsProvider.rename(v.getNamespace(), v.getTmpKeyName(), v.getKeyName());
            }
            default -> throw new UnsupportedOperationException("Unsupported destination sync mode");
          }
        } catch (Exception e) {
          LOGGER.error("Error while synchronizing keys: ", e);
        }
      });
      outputRecordCollector.accept(lastMessage);
    }

    redisOpsProvider.close();

  }

}
