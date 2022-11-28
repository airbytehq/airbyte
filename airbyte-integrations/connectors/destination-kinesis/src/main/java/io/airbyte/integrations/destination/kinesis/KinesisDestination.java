/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.kinesis;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * KinesisDestination class for configuring Kinesis as an Airbyte destination.
 */
public class KinesisDestination extends BaseConnector implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(KinesisDestination.class);

  public static void main(String[] args) throws Exception {
    new IntegrationRunner(new KinesisDestination()).run(args);
  }

  /**
   * Check Kinesis connection status with the provided Json configuration.
   *
   * @param config json configuration for connecting to Kinesis
   * @return AirbyteConnectionStatus status of the connection result.
   */
  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    KinesisStream kinesisStream = null;
    var streamName = "test_stream";
    try {
      var kinesisConfig = new KinesisConfig(config);
      kinesisStream = new KinesisStream(kinesisConfig);
      kinesisStream.createStream(streamName);
      var partitionKey = KinesisUtils.buildPartitionKey();
      kinesisStream.putRecord(streamName, partitionKey, "{}", e -> {});
      return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED);
    } catch (Exception e) {
      LOGGER.error("Error while trying to connect to Kinesis: ", e);
      return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.FAILED);
    } finally {
      if (kinesisStream != null) {
        try {
          kinesisStream.flush(e -> {});
          kinesisStream.deleteStream(streamName);
        } catch (Exception e) {
          LOGGER.error("Error while deleting kinesis stream: ", e);
        }
        kinesisStream.close();
      }
    }
  }

  /**
   * Returns an Airbyte message consumer which can be used to handle the incoming Airbyte messages.
   *
   * @param config json configuration for connecting to Kinesis
   * @param configuredCatalog of the incoming stream.
   * @param outputRecordCollector state collector.
   * @return KinesisMessageConsumer for consuming Airbyte messages and streaming them to Kinesis.
   */
  @Override
  public AirbyteMessageConsumer getConsumer(final JsonNode config,
                                            final ConfiguredAirbyteCatalog configuredCatalog,
                                            final Consumer<AirbyteMessage> outputRecordCollector) {
    final KinesisStream kinesisStream = new KinesisStream(new KinesisConfig(config));
    return new KinesisMessageConsumer(configuredCatalog, kinesisStream, outputRecordCollector);
  }

}
