/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redpanda;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.Map;
import java.util.Optional;
import org.apache.kafka.clients.admin.Admin;
import org.apache.kafka.clients.admin.AdminClient;
import org.apache.kafka.clients.admin.AdminClientConfig;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerConfig;

public class RedpandaConfig {

  // host1:port1,host2:port2,...
  private final String bootstrapServers;

  private final long bufferMemory;

  private final String compressionType;

  private final int retries;

  private final int batchSize;

  private final Optional<Integer> topicNumPartitions;

  private final Optional<Short> topicReplicationFactor;

  private final int socketConnectionSetupTimeoutMs;

  private final int socketConnectionSetupTimeoutMaxMs;

  private RedpandaConfig(String bootstrapServers,
                         long bufferMemory,
                         String compressionType,
                         int retries,
                         int batchSize,
                         Optional<Integer> topicNumPartitions,
                         Optional<Short> topicReplicationFactor,
                         int socketConnectionSetupTimeoutMs,
                         int socketConnectionSetupTimeoutMaxMs) {
    this.bootstrapServers = bootstrapServers;
    this.bufferMemory = bufferMemory;
    this.compressionType = compressionType;
    this.retries = retries;
    this.batchSize = batchSize;
    this.topicNumPartitions = topicNumPartitions;
    this.topicReplicationFactor = topicReplicationFactor;
    this.socketConnectionSetupTimeoutMs = socketConnectionSetupTimeoutMs;
    this.socketConnectionSetupTimeoutMaxMs = socketConnectionSetupTimeoutMaxMs;
  }

  public static RedpandaConfig createConfig(JsonNode jsonConfig) {
    return new RedpandaConfig(
        jsonConfig.get("bootstrap_servers").asText(),
        jsonConfig.get("buffer_memory").asLong(33554432L),
        jsonConfig.get("compression_type").asText("none"),
        jsonConfig.get("retries").asInt(5),
        jsonConfig.get("batch_size").asInt(16384),
        Optional.of(jsonConfig.get("topic_num_partitions").asInt(1)),
        Optional.of(((Integer) jsonConfig.get("topic_replication_factor").asInt(1)).shortValue()),
        jsonConfig.get("socket_connection_setup_timeout_ms").asInt(10000),
        jsonConfig.get("socket_connection_setup_timeout_max_ms").asInt(30000));
  }

  public KafkaProducer<String, JsonNode> createKafkaProducer() {
    return new KafkaProducer<>(Map.of(
        ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers,
        ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, "org.apache.kafka.common.serialization.StringSerializer",
        ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, "org.apache.kafka.connect.json.JsonSerializer",
        ProducerConfig.BUFFER_MEMORY_CONFIG, bufferMemory,
        ProducerConfig.COMPRESSION_TYPE_CONFIG, compressionType,
        ProducerConfig.RETRIES_CONFIG, retries,
        ProducerConfig.BATCH_SIZE_CONFIG, batchSize,
        ProducerConfig.SOCKET_CONNECTION_SETUP_TIMEOUT_MS_CONFIG, socketConnectionSetupTimeoutMs,
        ProducerConfig.SOCKET_CONNECTION_SETUP_TIMEOUT_MAX_MS_CONFIG, socketConnectionSetupTimeoutMaxMs));

  }

  public Admin createAdminClient() {
    return AdminClient.create(Map.of(
        AdminClientConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers,
        AdminClientConfig.RETRIES_CONFIG, retries,
        AdminClientConfig.SOCKET_CONNECTION_SETUP_TIMEOUT_MS_CONFIG, socketConnectionSetupTimeoutMs,
        AdminClientConfig.SOCKET_CONNECTION_SETUP_TIMEOUT_MAX_MS_CONFIG, socketConnectionSetupTimeoutMaxMs));
  }

  public Optional<Integer> topicNumPartitions() {
    return topicNumPartitions;
  }

  public Optional<Short> topicReplicationFactor() {
    return topicReplicationFactor;
  }

}
