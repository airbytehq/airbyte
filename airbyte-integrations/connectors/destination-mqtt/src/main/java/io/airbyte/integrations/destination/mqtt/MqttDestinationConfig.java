/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mqtt;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.UUID;
import org.eclipse.paho.client.mqttv3.MqttConnectOptions;

public class MqttDestinationConfig {

  private final String clientId;
  private final String serverUri;
  private final String topicPattern;
  private final String testTopic;
  private final MqttConnectOptions options;
  private final boolean retained;
  private final boolean sync;
  private final int qOs;

  private MqttDestinationConfig(final JsonNode config) {
    this.clientId = buildClientId(config);
    this.serverUri = buildServerUri(config);
    this.testTopic = buildTestTopic(config);
    this.topicPattern = buildTopicPattern(config);
    this.options = buildMqttConnectOptions(config);
    this.retained = isRetained(config);
    this.sync = isSyncProducer(config);
    this.qOs = buildQos(config);
  }

  public static MqttDestinationConfig getMqttDestinationConfig(final JsonNode config) {
    return new MqttDestinationConfig(config);
  }

  public String getClientId() {
    return clientId;
  }

  public int getQos() {
    return qOs;
  }

  public MqttConnectOptions getMqttConnectOptions() {
    return options;
  }

  public String getServerUri() {
    return serverUri;
  }

  public String getTestTopic() {
    return testTopic;
  }

  public String getTopicPattern() {
    return topicPattern;
  }

  public boolean isSync() {
    return sync;
  }

  public boolean isRetainedMessage() {
    return retained;
  }

  private String buildClientId(final JsonNode config) {
    if (config.has("client_id")) {
      return config.get("client_id").asText();
    }
    return "airbyte-" + UUID.randomUUID();
  }

  private MqttConnectOptions buildMqttConnectOptions(final JsonNode config) {
    final MqttConnectOptions options = new MqttConnectOptions();
    options.setConnectionTimeout(config.get("connect_timeout").intValue());
    options.setAutomaticReconnect(config.get("automatic_reconnect").booleanValue());
    options.setCleanSession(config.get("clean_session").booleanValue());
    if (config.has("username") && !config.get("username").asText().isBlank()) {
      options.setUserName(config.get("username").asText());
    }
    if (config.has("password") && !config.get("password").asText().isBlank()) {
      options.setPassword(config.get("password").asText().toCharArray());
    }

    if (config.has("max_in_flight") && !config.get("max_in_flight").asText().isBlank()) {
      options.setMaxInflight(config.get("max_in_flight").asInt());
    }

    return options;
  }

  private String buildServerUri(final JsonNode config) {
    return String.format("%s://%s:%s",
        config.get("use_tls").asBoolean() ? "ssl" : "tcp",
        config.get("broker_host").asText(),
        config.get("broker_port").intValue());
  }

  private String buildTestTopic(final JsonNode config) {
    return config.has("test_topic") ? config.get("test_topic").asText() : "";
  }

  private String buildTopicPattern(final JsonNode config) {
    return config.get("topic_pattern").asText();
  }

  private boolean isRetained(final JsonNode config) {
    return config.get("message_retained").asBoolean();
  }

  private boolean isSyncProducer(final JsonNode config) {
    return config.get("publisher_sync").asBoolean();
  }

  private int buildQos(final JsonNode config) {
    return MessageQoS.valueOf(config.get("message_qos").asText()).getQos();
  }

  private enum MessageQoS {

    AT_MOST_ONCE(0),
    AT_LEAST_ONCE(1),
    EXACTLY_ONCE(2);

    private final int qos;

    MessageQoS(final int qos) {
      this.qos = qos;
    }

    public int getQos() {
      return qos;
    }

  }

}
