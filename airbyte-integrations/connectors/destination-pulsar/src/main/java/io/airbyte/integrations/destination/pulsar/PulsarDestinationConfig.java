/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.pulsar;

import com.fasterxml.jackson.databind.JsonNode;

import java.util.Map;

import com.google.common.collect.ImmutableMap;
import org.apache.pulsar.client.api.CompressionType;
import org.apache.pulsar.client.api.schema.RecordSchemaBuilder;
import org.apache.pulsar.client.api.schema.SchemaBuilder;
import org.apache.pulsar.common.schema.SchemaInfo;
import org.apache.pulsar.common.schema.SchemaType;

public class PulsarDestinationConfig {

  private final String topicPattern;
  private final boolean sync;
  private final Map<String, Object> producerConfig;
  private final String serviceUrl;

  private PulsarDestinationConfig(final String topicPattern, final boolean sync, final JsonNode config) {
    this.topicPattern = topicPattern;
    this.sync = sync;
    this.producerConfig = buildProducerConfig(config);
    this.serviceUrl = buildServiceUrl(config);
  }

  public static PulsarDestinationConfig getPulsarDestinationConfig(final JsonNode config) {
    return new PulsarDestinationConfig(
        config.get("topic_pattern").asText(),
        config.has("sync_producer") && config.get("sync_producer").asBoolean(),
        config);
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

  public String getTopicPattern() {
    return topicPattern;
  }

  public boolean isSync() {
    return sync;
  }

  private String buildServiceUrl(final JsonNode config) {
    return "pulsar" + (config.get("use_tls").asBoolean() ? "+ssl" : "") + "://" + config.get("pulsar_brokers").asText();
  }

  private Map<String, Object> buildProducerConfig(final JsonNode config) {
    final ImmutableMap.Builder<String, Object> conf = ImmutableMap.builder();
    if (config.has("producer_name")) {
      conf.put("producerName", config.get("producer_name").asText());
    }
    conf.put("batchingEnabled", config.get("batching_enabled").asBoolean());
    conf.put("batchingMaxMessages", config.get("batching_max_messages").asInt());
    conf.put("batchingMaxPublishDelayMicros", config.get("batching_max_publish_delay").asInt() * 1000);
    conf.put("blockIfQueueFull", config.get("block_if_queue_full").asBoolean());
    conf.put("compressionType", CompressionType.valueOf(config.get("compression_type").asText()));

    return conf.build();
  }

}
