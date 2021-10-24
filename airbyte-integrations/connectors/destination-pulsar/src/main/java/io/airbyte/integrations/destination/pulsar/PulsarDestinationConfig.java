/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.pulsar;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.concurrent.TimeUnit;

import org.apache.pulsar.client.api.CompressionType;
import org.apache.pulsar.client.api.Producer;
import org.apache.pulsar.client.api.ProducerAccessMode;
import org.apache.pulsar.client.api.PulsarClient;
import org.apache.pulsar.client.api.PulsarClientException;
import org.apache.pulsar.client.api.Schema;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PulsarDestinationConfig {

  protected static final Logger LOGGER = LoggerFactory.getLogger(PulsarDestinationConfig.class);

  private final String topicPattern;
  private final boolean sync;
  private final ProducerConfig producerConfig;

  private PulsarDestinationConfig(final String topicPattern, final boolean sync, final JsonNode config) {
    this.topicPattern = topicPattern;
    this.sync = sync;
    this.producerConfig = buildProducerConfig(config);
  }

  public static PulsarDestinationConfig getPulsarDestinationConfig(final JsonNode config) {
    return new PulsarDestinationConfig(
        config.get("topic_pattern").asText(),
        config.has("sync_producer") && config.get("sync_producer").asBoolean(),
        config);
  }

  private ProducerConfig buildProducerConfig(final JsonNode config) {
    try {
      return new ProducerConfig(config);
    } catch (PulsarClientException e) {
      LOGGER.error("Error creating Pulsar producer.", e);
      throw new RuntimeException("Cannot create Pulsar producer.", e);
    }
  }

  public String getTopicPattern() {
    return topicPattern;
  }

  public boolean isSync() {
    return sync;
  }

  public Producer<JsonNode> getProducer(final String topic) {
    try {
      return producerConfig.createProducer(topic);
    } catch (PulsarClientException e) {
      LOGGER.error("Error creating Pulsar producer.", e);
      throw new RuntimeException("Cannot create Pulsar producer.", e);
    }
  }

  private static class ProducerConfig {

    private final String pulsarBrokers;
    private final String producerName;
    private final ProducerAccessMode accessMode;
    private final CompressionType compressionType;
    private final boolean useTls;
    private final boolean enableBatching;
    private final boolean blockIfQueueFull;
    private final boolean autoUpdatePartitions;
    private final boolean enableChunking;
    private final int autoUpdatePartitionsInterval;
    private final int batchingMaxPublishDelay;
    private final int batchingMaxMessages;

    private ProducerConfig(final JsonNode config) throws PulsarClientException {
      this.pulsarBrokers = config.get("pulsar_brokers").asText();
      this.producerName = config.has("producer_name") ? config.get("producer_name").asText() : "";
      this.accessMode = ProducerAccessMode.valueOf(config.get("access_mode").asText());
      this.compressionType = CompressionType.valueOf(config.get("compression_type").asText());
      this.useTls = config.get("use_tls").asBoolean();
      this.enableBatching = config.get("enable_batching").asBoolean();
      this.blockIfQueueFull = config.get("block_if_queue_full").asBoolean();
      this.autoUpdatePartitions = config.get("auto_update_partitions").asBoolean();
      this.enableChunking = config.get("enable_chunking").asBoolean();
      this.autoUpdatePartitionsInterval = config.get("auto_update_partitions_interval").asInt();
      this.batchingMaxPublishDelay = config.get("batching_max_publish_delay").asInt();
      this.batchingMaxMessages = config.get("batching_max_messages").asInt();
    }

    private Producer<JsonNode> createProducer(final String topic) throws PulsarClientException {
      final String serviceUrl = "pulsar" + (useTls ? "+ssl" : "") + "://" + pulsarBrokers;
      final PulsarClient client = PulsarClient.builder()
        .serviceUrl(serviceUrl)
        .build();

      return client.newProducer(Schema.JSON(JsonNode.class))
        .topic(topic)
        .producerName(producerName)
        .accessMode(accessMode)
        .compressionType(compressionType)
        .enableBatching(enableBatching)
        .batchingMaxPublishDelay(batchingMaxPublishDelay, TimeUnit.MILLISECONDS)
        .batchingMaxMessages(batchingMaxMessages)
        .enableChunking(enableChunking)
        .blockIfQueueFull(blockIfQueueFull)
        .autoUpdatePartitions(autoUpdatePartitions)
        .autoUpdatePartitionsInterval(autoUpdatePartitionsInterval, TimeUnit.SECONDS)
        .create();
    }
  }

}
