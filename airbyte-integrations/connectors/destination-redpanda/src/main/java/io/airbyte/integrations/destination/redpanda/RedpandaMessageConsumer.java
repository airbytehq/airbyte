/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redpanda;

import static io.airbyte.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_ID;
import static io.airbyte.integrations.base.JavaBaseConstants.COLUMN_NAME_DATA;
import static io.airbyte.integrations.base.JavaBaseConstants.COLUMN_NAME_EMITTED_AT;

import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.time.Instant;
import java.util.Map;
import java.util.UUID;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RedpandaMessageConsumer extends FailureTrackingAirbyteMessageConsumer {

  private static final Logger LOGGER = LoggerFactory.getLogger(RedpandaMessageConsumer.class);

  private final Consumer<AirbyteMessage> outputRecordCollector;

  private final RedpandaOperations redpandaOperations;

  private final RedpandaConfig redpandaConfig;

  private final Map<AirbyteStreamNameNamespacePair, RedpandaWriteConfig> redpandaWriteConfigs;

  public RedpandaMessageConsumer(ConfiguredAirbyteCatalog configuredCatalog,
                                 RedpandaOperations redpandaOperations,
                                 RedpandaConfig redpandaConfig,
                                 Consumer<AirbyteMessage> outputRecordCollector) {
    this.outputRecordCollector = outputRecordCollector;
    this.redpandaOperations = redpandaOperations;
    this.redpandaConfig = redpandaConfig;
    this.redpandaWriteConfigs = configuredCatalog.getStreams().stream()
        .collect(
            Collectors.toUnmodifiableMap(AirbyteStreamNameNamespacePair::fromConfiguredAirbyteSteam,
                str -> new RedpandaWriteConfig(
                    new RedpandaNameTransformer().topicName(str.getStream().getNamespace(),
                        str.getStream().getName()),
                    str.getDestinationSyncMode())));
  }

  @Override
  protected void startTracked() {
    redpandaOperations.createTopic(redpandaWriteConfigs.values().stream()
        .map(wc -> new RedpandaOperations.TopicInfo(wc.topicName(), redpandaConfig.topicNumPartitions(),
            redpandaConfig.topicReplicationFactor()))
        .collect(Collectors.toSet()));
  }

  @Override
  protected void acceptTracked(AirbyteMessage message) {
    if (message.getType() == AirbyteMessage.Type.RECORD) {
      var messageRecord = message.getRecord();

      var streamConfig =
          redpandaWriteConfigs.get(AirbyteStreamNameNamespacePair.fromRecordMessage(messageRecord));

      if (streamConfig == null) {
        throw new IllegalArgumentException("Unrecognized destination stream");
      }

      String key = UUID.randomUUID().toString();

      var data = Jsons.jsonNode(Map.of(
          COLUMN_NAME_AB_ID, key,
          COLUMN_NAME_DATA, messageRecord.getData(),
          COLUMN_NAME_EMITTED_AT, Instant.now()));

      var topic = streamConfig.topicName();

      redpandaOperations.putRecord(topic, key, data, e -> {
        LOGGER.error("Error while sending record to Redpanda with reason ", e);
        try {
          throw e;
        } catch (Exception ex) {
          throw new RuntimeException(ex);
        }
      });
    } else if (message.getType() == AirbyteMessage.Type.STATE) {
      outputRecordCollector.accept(message);
    } else {
      LOGGER.warn("Unsupported airbyte message type: {}", message.getType());
    }
  }

  @Override
  protected void close(boolean hasFailed) {
    redpandaOperations.close();
  }

}
