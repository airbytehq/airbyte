/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mqtt;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Charsets;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.stream.Collectors;
import org.eclipse.paho.client.mqttv3.IMqttActionListener;
import org.eclipse.paho.client.mqttv3.IMqttAsyncClient;
import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken;
import org.eclipse.paho.client.mqttv3.IMqttToken;
import org.eclipse.paho.client.mqttv3.MqttAsyncClient;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.eclipse.paho.client.mqttv3.persist.MemoryPersistence;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MqttRecordConsumer extends FailureTrackingAirbyteMessageConsumer {

  private static final Logger LOGGER = LoggerFactory.getLogger(MqttRecordConsumer.class);

  private final MqttDestinationConfig config;
  private final Map<AirbyteStreamNameNamespacePair, String> topicMap;
  private final ConfiguredAirbyteCatalog catalog;
  private final Consumer<AirbyteMessage> outputRecordCollector;
  private final IMqttAsyncClient client;

  private AirbyteMessage lastStateMessage = null;

  public MqttRecordConsumer(final MqttDestinationConfig mqttDestinationConfig,
                            final ConfiguredAirbyteCatalog catalog,
                            final Consumer<AirbyteMessage> outputRecordCollector) {
    this.config = mqttDestinationConfig;
    this.topicMap = new HashMap<>();
    this.catalog = catalog;
    this.outputRecordCollector = outputRecordCollector;
    this.client = buildMqttClient();
  }

  private IMqttAsyncClient buildMqttClient() {
    try {
      return new MqttAsyncClient(config.getServerUri(), config.getClientId(), new MemoryPersistence());
    } catch (MqttException e) {
      throw new RuntimeException("Error creating MQTT client", e);
    }
  }

  @Override
  protected void startTracked() {
    try {
      client.connect(config.getMqttConnectOptions()).waitForCompletion();
    } catch (MqttException e) {
      throw new RuntimeException("Error connecting to MQTT broker", e);
    }
    topicMap.putAll(buildTopicMap());
  }

  @Override
  protected void acceptTracked(final AirbyteMessage airbyteMessage) {
    if (airbyteMessage.getType() == AirbyteMessage.Type.STATE) {
      lastStateMessage = airbyteMessage;
    } else if (airbyteMessage.getType() == AirbyteMessage.Type.RECORD) {
      final AirbyteRecordMessage recordMessage = airbyteMessage.getRecord();
      final String topic = topicMap.get(AirbyteStreamNameNamespacePair.fromRecordMessage(recordMessage));

      final String key = UUID.randomUUID().toString();
      final JsonNode payload = Jsons.jsonNode(ImmutableMap.of(
          MqttDestination.COLUMN_NAME_AB_ID, key,
          MqttDestination.COLUMN_NAME_STREAM, recordMessage.getStream(),
          MqttDestination.COLUMN_NAME_EMITTED_AT, recordMessage.getEmittedAt(),
          MqttDestination.COLUMN_NAME_DATA, recordMessage.getData()));

      final MqttMessage message = new MqttMessage(payload.toString().getBytes(Charsets.UTF_8));
      message.setRetained(config.isRetainedMessage());
      message.setQos(config.getQos());

      sendRecord(topic, message);
    } else {
      LOGGER.warn("Unexpected message: " + airbyteMessage.getType());
    }
  }

  Map<AirbyteStreamNameNamespacePair, String> buildTopicMap() {
    return catalog.getStreams().stream()
        .map(stream -> AirbyteStreamNameNamespacePair.fromAirbyteStream(stream.getStream()))
        .collect(Collectors.toMap(Function.identity(), pair -> config.getTopicPattern()
            .replaceAll("\\{namespace}", Optional.ofNullable(pair.getNamespace()).orElse(""))
            .replaceAll("\\{stream}", Optional.ofNullable(pair.getName()).orElse("")),
            (existing, newValue) -> existing));
  }

  private void sendRecord(final String topic, final MqttMessage message) {
    try {
      final IMqttDeliveryToken token = client.publish(topic, message, null, new MessageActionListener(outputRecordCollector, lastStateMessage));
      if (config.isSync()) {
        token.waitForCompletion();
      }
    } catch (MqttException e) {
      LOGGER.error("Error sending message to topic '{}'.", topic, e);
      throw new RuntimeException("Cannot send message to MQTT. Error: " + e.getMessage(), e);
    }
  }

  @Override
  protected void close(final boolean hasFailed) {
    Exceptions.swallow(client::disconnectForcibly);
    Exceptions.swallow(client::close);

    if (lastStateMessage != null) {
      outputRecordCollector.accept(lastStateMessage);
    }
  }

  private static class MessageActionListener implements IMqttActionListener {

    private final AirbyteMessage lastStateMessage;
    private final Consumer<AirbyteMessage> outputRecordCollector;

    MessageActionListener(Consumer<AirbyteMessage> outputRecordCollector, AirbyteMessage lastStateMessage) {
      this.outputRecordCollector = outputRecordCollector;
      this.lastStateMessage = lastStateMessage;
    }

    @Override
    public void onSuccess(IMqttToken asyncActionToken) {
      if (lastStateMessage != null) {
        outputRecordCollector.accept(lastStateMessage);
      }
    }

    @Override
    public void onFailure(IMqttToken asyncActionToken, Throwable exception) {
      throw new RuntimeException("Cannot deliver message with ID '" + asyncActionToken.getMessageId() + "'", exception);
    }

  }

}
