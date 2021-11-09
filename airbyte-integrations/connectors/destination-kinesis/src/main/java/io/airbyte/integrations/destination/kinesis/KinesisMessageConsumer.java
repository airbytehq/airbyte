/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.kinesis;

import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.time.Instant;
import java.util.Map;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class KinesisMessageConsumer extends FailureTrackingAirbyteMessageConsumer {

  private static final Logger LOGGER = LoggerFactory.getLogger(KinesisMessageConsumer.class);

  private final Consumer<AirbyteMessage> outputRecordCollector;

  private final KinesisStream kinesisStream;

  private final Map<AirbyteStreamNameNamespacePair, KinesisStreamConfig> kinesisStreams;

  private AirbyteMessage lastMessage = null;

  public KinesisMessageConsumer(KinesisConfig kinesisConfig,
                                ConfiguredAirbyteCatalog configuredCatalog,
                                Consumer<AirbyteMessage> outputRecordCollector) {
    this.outputRecordCollector = outputRecordCollector;
    this.kinesisStream = new KinesisStream(kinesisConfig);
    var nameTransformer = new KinesisNameTransformer();
    this.kinesisStreams = configuredCatalog.getStreams().stream()
        .collect(Collectors.toUnmodifiableMap(
            AirbyteStreamNameNamespacePair::fromConfiguredAirbyteSteam,
            k -> new KinesisStreamConfig(
                nameTransformer.streamName(k.getStream().getNamespace(), k.getStream().getName()),
                k.getDestinationSyncMode())));
  }

  @Override
  protected void startTracked() {
    kinesisStreams.forEach((k, v) -> kinesisStream.createStream(v.getStreamName()));
  }

  @Override
  protected void acceptTracked(AirbyteMessage message) {
    if (message.getType() == AirbyteMessage.Type.RECORD) {
      var messageRecord = message.getRecord();

      var streamConfig =
          kinesisStreams.get(AirbyteStreamNameNamespacePair.fromRecordMessage(messageRecord));

      if (streamConfig == null) {
        throw new IllegalArgumentException("Unrecognized destination stream");
      }

      var partitionKey = KinesisUtils.buildPartitionKey();

      var data = Jsons.jsonNode(Map.of(
          JavaBaseConstants.COLUMN_NAME_AB_ID, partitionKey,
          JavaBaseConstants.COLUMN_NAME_DATA, Jsons.serialize(messageRecord.getData()),
          JavaBaseConstants.COLUMN_NAME_EMITTED_AT, Instant.now()));

      kinesisStream.putRecord(streamConfig.getStreamName(), partitionKey, Jsons.serialize(data));
    } else if (message.getType() == AirbyteMessage.Type.STATE) {
      this.lastMessage = message;
    } else {
      LOGGER.warn("Unsupported airbyte message type: {}", message.getType());
    }
  }

  @Override
  protected void close(boolean hasFailed) {
    if (!hasFailed) {
      kinesisStream.flush();
      this.outputRecordCollector.accept(lastMessage);
    }
    kinesisStream.close();
  }

}
