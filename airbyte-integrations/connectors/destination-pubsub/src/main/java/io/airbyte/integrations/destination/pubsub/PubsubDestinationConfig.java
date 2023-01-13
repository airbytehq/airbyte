/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.pubsub;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.api.gax.batching.BatchingSettings;
import com.google.auth.oauth2.ServiceAccountCredentials;
import com.google.common.base.Charsets;
import com.google.common.base.Function;
import com.google.pubsub.v1.TopicName;
import io.airbyte.commons.json.Jsons;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import org.threeten.bp.Duration;

public class PubsubDestinationConfig {

  static final String CONFIG_TOPIC_ID = "topic_id";
  static final String CONFIG_PROJECT_ID = "project_id";
  static final String CONFIG_CREDS = "credentials_json";
  static final String CONFIG_ORDERING_ENABLED = "ordering_enabled";
  static final String CONFIG_BATCHING_ENABLED = "batching_enabled";
  static final String CONFIG_BATCHING_DELAY_THRESHOLD = "batching_delay_threshold";
  static final String CONFIG_BATCHING_ELEMENT_COUNT_THRESHOLD = "batching_element_count_threshold";
  static final String CONFIG_BATCHING_REQUEST_BYTES_THRESHOLD = "batching_request_bytes_threshold";
  private final TopicName topic;
  private final ServiceAccountCredentials credentials;
  private final boolean orderingEnabled;
  private final BatchingSettings batchingSettings;

  private PubsubDestinationConfig(TopicName topic,
                                  ServiceAccountCredentials credentials,
                                  boolean orderingEnabled,
                                  BatchingSettings batchingSettings) {
    this.topic = topic;
    this.credentials = credentials;
    this.orderingEnabled = orderingEnabled;
    this.batchingSettings = batchingSettings;
  }

  public static PubsubDestinationConfig fromJsonNode(final JsonNode config) throws IOException {
    final String projectId = config.get(CONFIG_PROJECT_ID).asText();
    final String topicName = config.get(CONFIG_TOPIC_ID).asText();
    final TopicName topic = TopicName.of(projectId, topicName);
    final String credentialsString = config.get(CONFIG_CREDS).isObject()
        ? Jsons.serialize(config.get(CONFIG_CREDS))
        : config.get(CONFIG_CREDS).asText();
    final ServiceAccountCredentials credentials = ServiceAccountCredentials
        .fromStream(new ByteArrayInputStream(credentialsString.getBytes(Charsets.UTF_8)));

    final boolean orderingEnabled = config.get(CONFIG_ORDERING_ENABLED).asBoolean();

    final var batchingSetting = BatchingSettings.newBuilder()
        .setIsEnabled(config.get(CONFIG_BATCHING_ENABLED).asBoolean())
        .setDelayThreshold(Duration.ofMillis(getOrDefault(config, CONFIG_BATCHING_DELAY_THRESHOLD, JsonNode::asLong, 1L)))
        .setRequestByteThreshold(getOrDefault(config, CONFIG_BATCHING_REQUEST_BYTES_THRESHOLD, JsonNode::asLong, 1L))
        .setElementCountThreshold(getOrDefault(config, CONFIG_BATCHING_ELEMENT_COUNT_THRESHOLD, JsonNode::asLong, 1L))
        .build();

    return new PubsubDestinationConfig(topic, credentials, orderingEnabled, batchingSetting);
  }

  private static <T> T getOrDefault(JsonNode node, String key, Function<JsonNode, T> consumer, T defaultValue) {
    var value = node.get(key);
    if (value != null) {
      return consumer.apply(value);
    } else {
      return defaultValue;
    }
  }

  public BatchingSettings getBatchingSettings() {
    return batchingSettings;
  }

  public boolean isOrderingEnabled() {
    return orderingEnabled;
  }

  public ServiceAccountCredentials getCredentials() {
    return credentials;
  }

  public TopicName getTopic() {
    return topic;
  }

}
