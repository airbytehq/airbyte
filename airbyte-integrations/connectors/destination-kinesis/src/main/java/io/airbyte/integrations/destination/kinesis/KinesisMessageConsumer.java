/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.kinesis;

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

/**
 * KinesisMessageConsumer class for handling incoming Airbyte messages.
 */
public class KinesisMessageConsumer extends FailureTrackingAirbyteMessageConsumer {

  private static final Logger LOGGER = LoggerFactory.getLogger(KinesisMessageConsumer.class);

  private final Consumer<AirbyteMessage> outputRecordCollector;

  private final KinesisStream kinesisStream;

  private final Map<AirbyteStreamNameNamespacePair, KinesisStreamConfig> kinesisStreams;

  public KinesisMessageConsumer(final ConfiguredAirbyteCatalog configuredCatalog,
                                final KinesisStream kinesisStream,
                                final Consumer<AirbyteMessage> outputRecordCollector) {
    this.outputRecordCollector = outputRecordCollector;
    this.kinesisStream = kinesisStream;
    var nameTransformer = new KinesisNameTransformer();
    this.kinesisStreams = configuredCatalog.getStreams().stream()
        .collect(Collectors.toUnmodifiableMap(
            AirbyteStreamNameNamespacePair::fromConfiguredAirbyteSteam,
            k -> new KinesisStreamConfig(
                nameTransformer.streamName(k.getStream().getNamespace(), k.getStream().getName()),
                k.getDestinationSyncMode())));
  }

  /**
   * Start tracking the incoming Airbyte streams by creating the needed Kinesis streams.
   */
  @Override
  protected void startTracked() {
    kinesisStreams.forEach((k, v) -> kinesisStream.createStream(v.getStreamName()));
  }

  /**
   * Handle an incoming Airbyte message by serializing it to the appropriate Kinesis structure and
   * sending it to the stream.
   *
   * @param message received from the Airbyte source.
   */
  @Override
  protected void acceptTracked(final AirbyteMessage message) {
    if (message.getType() == AirbyteMessage.Type.RECORD) {
      var messageRecord = message.getRecord();

      var streamConfig =
          kinesisStreams.get(AirbyteStreamNameNamespacePair.fromRecordMessage(messageRecord));

      if (streamConfig == null) {
        throw new IllegalArgumentException("Unrecognized destination stream");
      }

      var partitionKey = KinesisUtils.buildPartitionKey();

      var data = Jsons.jsonNode(Map.of(
          KinesisRecord.COLUMN_NAME_AB_ID, partitionKey,
          KinesisRecord.COLUMN_NAME_DATA, Jsons.serialize(messageRecord.getData()),
          KinesisRecord.COLUMN_NAME_EMITTED_AT, Instant.now()));

      var streamName = streamConfig.getStreamName();
      kinesisStream.putRecord(streamName, partitionKey, Jsons.serialize(data), e -> {
        LOGGER.error("Error while streaming data to Kinesis", e);
        // throw exception and end sync?
      });
    } else if (message.getType() == AirbyteMessage.Type.STATE) {
      outputRecordCollector.accept(message);
    } else {
      LOGGER.warn("Unsupported airbyte message type: {}", message.getType());
    }
  }

  /**
   * Flush the Kinesis stream if there are any remaining messages to be sent and close the client as a
   * terminal operation.
   *
   * @param hasFailed flag for indicating if the operation has failed.
   */
  @Override
  protected void close(final boolean hasFailed) {
    try {
      if (!hasFailed) {
        kinesisStream.flush(e -> {
          LOGGER.error("Error while streaming data to Kinesis", e);
        });
      }
    } finally {
      kinesisStream.close();
    }
  }

}
