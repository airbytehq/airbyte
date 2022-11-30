/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.pulsar;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import java.util.Map;
import org.apache.pulsar.client.api.CompressionType;
import org.apache.pulsar.client.api.schema.RecordSchemaBuilder;
import org.apache.pulsar.client.api.schema.SchemaBuilder;
import org.apache.pulsar.common.schema.SchemaInfo;
import org.apache.pulsar.common.schema.SchemaType;

public class PulsarDestinationConfig {

  private final String serviceUrl;
  private final String topicPattern;
  private final String topicPrefix;
  private final String testTopic;
  private final Map<String, Object> producerConfig;
  private final boolean sync;

  private PulsarDestinationConfig(final JsonNode config) {
    this.serviceUrl = buildServiceUrl(config);
    this.topicPattern = buildTopicPattern(config);
    this.topicPrefix = buildTopicPrefix(config);
    this.testTopic = buildTestTopic(config);
    this.producerConfig = buildProducerConfig(config);
    this.sync = isSyncProducer(config);
  }

  public static PulsarDestinationConfig getPulsarDestinationConfig(final JsonNode config) {
    return new PulsarDestinationConfig(config);
  }

  public Map<String, Object> getProducerConfig() {
    return producerConfig;
  }

  public String getServiceUrl() {
    return serviceUrl;
  }

  public static SchemaInfo getSchemaInfo() {
    RecordSchemaBuilder recordSchemaBuilder = SchemaBuilder.record("airbyte");
    recordSchemaBuilder.field(PulsarDestination.COLUMN_NAME_AB_ID).type(SchemaType.STRING).required();
    recordSchemaBuilder.field(PulsarDestination.COLUMN_NAME_STREAM).type(SchemaType.STRING).required();
    recordSchemaBuilder.field(PulsarDestination.COLUMN_NAME_EMITTED_AT).type(SchemaType.TIMESTAMP).required();
    recordSchemaBuilder.field(PulsarDestination.COLUMN_NAME_DATA).type(SchemaType.BYTES).required();

    return recordSchemaBuilder.build(SchemaType.JSON);
  }

  public String uriForTopic(final String topic) {
    return topicPrefix + topic;
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

  private String buildServiceUrl(final JsonNode config) {
    return String.format("pulsar%s://%s",
        config.get("use_tls").asBoolean() ? "+ssl" : "",
        config.get("brokers").asText());
  }

  private String buildTestTopic(final JsonNode config) {
    return config.has("test_topic") ? config.get("test_topic").asText() : "";
  }

  private String buildTopicPattern(final JsonNode config) {
    return config.get("topic_pattern").asText();
  }

  private String buildTopicPrefix(final JsonNode config) {
    return String.format("%s://%s/%s/",
        config.get("topic_type").asText(),
        config.get("topic_tenant").asText(),
        config.get("topic_namespace").asText());
  }

  private Map<String, Object> buildProducerConfig(final JsonNode config) {
    final ImmutableMap.Builder<String, Object> conf = ImmutableMap.builder();
    if (config.has("producer_name")) {
      conf.put("producerName", config.get("producer_name").asText());
    }
    conf.put("compressionType", CompressionType.valueOf(config.get("compression_type").asText()));
    conf.put("sendTimeoutMs", config.get("send_timeout_ms").asInt());
    conf.put("maxPendingMessages", config.get("max_pending_messages").asInt());
    conf.put("maxPendingMessagesAcrossPartitions", config.get("max_pending_messages_across_partitions").asInt());
    conf.put("batchingEnabled", config.get("batching_enabled").asBoolean());
    conf.put("batchingMaxMessages", config.get("batching_max_messages").asInt());
    conf.put("batchingMaxPublishDelayMicros", config.get("batching_max_publish_delay").asInt() * 1000);
    conf.put("blockIfQueueFull", config.get("block_if_queue_full").asBoolean());

    return conf.build();
  }

  private boolean isSyncProducer(final JsonNode config) {
    return config.has("producer_sync") && config.get("producer_sync").asBoolean();
  }

}
