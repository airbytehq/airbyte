/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mqtt;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Charsets;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.UUID;
import java.util.function.Consumer;
import org.eclipse.paho.client.mqttv3.IMqttAsyncClient;
import org.eclipse.paho.client.mqttv3.MqttAsyncClient;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MqttDestination extends BaseConnector implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(MqttDestination.class);

  public static final String COLUMN_NAME_AB_ID = JavaBaseConstants.COLUMN_NAME_AB_ID;
  public static final String COLUMN_NAME_EMITTED_AT = JavaBaseConstants.COLUMN_NAME_EMITTED_AT;
  public static final String COLUMN_NAME_DATA = JavaBaseConstants.COLUMN_NAME_DATA;
  public static final String COLUMN_NAME_STREAM = "_airbyte_stream";

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    try {
      final MqttDestinationConfig mqttConfig = MqttDestinationConfig.getMqttDestinationConfig(config);
      final String testTopic = mqttConfig.getTestTopic();
      if (!testTopic.isBlank()) {
        try (final IMqttAsyncClient client = new MqttAsyncClient(mqttConfig.getServerUri(), mqttConfig.getClientId())) {
          client.connect(mqttConfig.getMqttConnectOptions()).waitForCompletion();

          final String key = UUID.randomUUID().toString();
          final JsonNode payload = Jsons.jsonNode(ImmutableMap.of(
              COLUMN_NAME_AB_ID, key,
              COLUMN_NAME_STREAM, "test-topic-stream",
              COLUMN_NAME_EMITTED_AT, System.currentTimeMillis(),
              COLUMN_NAME_DATA, Jsons.jsonNode(ImmutableMap.of("test-key", "test-value"))));

          final MqttMessage message = new MqttMessage(payload.toString().getBytes(Charsets.UTF_8));
          message.setQos(mqttConfig.getQos());
          message.setRetained(mqttConfig.isRetainedMessage());

          client.publish(testTopic, message).getMessage();
          client.disconnectForcibly();

          LOGGER.info("Successfully sent message with key '{}' to MQTT broker for topic '{}'.", key, testTopic);
        }
      }
      return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    } catch (final Exception e) {
      LOGGER.error("Exception attempting to connect to the MQTT broker: ", e);
      return new AirbyteConnectionStatus()
          .withStatus(Status.FAILED)
          .withMessage("Could not connect to the MQTT broker with provided configuration. \n" + e.getMessage());
    }
  }

  @Override
  public AirbyteMessageConsumer getConsumer(final JsonNode config,
                                            final ConfiguredAirbyteCatalog catalog,
                                            final Consumer<AirbyteMessage> outputRecordCollector) {
    return new MqttRecordConsumer(MqttDestinationConfig.getMqttDestinationConfig(config),
        catalog,
        outputRecordCollector);
  }

  public static void main(final String[] args) throws Exception {
    final Destination destination = new MqttDestination();
    LOGGER.info("Starting destination: {}", MqttDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("Completed destination: {}", MqttDestination.class);
  }

}
