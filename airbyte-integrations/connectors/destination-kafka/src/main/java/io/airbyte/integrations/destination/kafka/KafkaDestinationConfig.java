/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.kafka;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import java.util.Map;
import java.util.stream.Collectors;
import org.apache.kafka.clients.CommonClientConfigs;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.common.config.SaslConfigs;
import org.apache.kafka.common.serialization.StringSerializer;
import org.apache.kafka.connect.json.JsonSerializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class KafkaDestinationConfig {

  protected static final Logger LOGGER = LoggerFactory.getLogger(KafkaDestinationConfig.class);

  private final String topicPattern;
  private final boolean sync;
  private final KafkaProducer<String, JsonNode> producer;

  private KafkaDestinationConfig(final String topicPattern, final boolean sync, final JsonNode config) {
    this.topicPattern = topicPattern;
    this.sync = sync;
    this.producer = buildKafkaProducer(config);
  }

  public static KafkaDestinationConfig getKafkaDestinationConfig(final JsonNode config) {
    return new KafkaDestinationConfig(
        config.get("topic_pattern").asText(),
        config.has("sync_producer") && config.get("sync_producer").asBoolean(),
        config);
  }

  private KafkaProducer<String, JsonNode> buildKafkaProducer(final JsonNode config) {
    final Map<String, Object> props = ImmutableMap.<String, Object>builder()
        .put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, config.get("bootstrap_servers").asText())
        .putAll(propertiesByProtocol(config))
        .put(ProducerConfig.CLIENT_ID_CONFIG,
            config.has("client_id") ? config.get("client_id").asText() : "")
        .put(ProducerConfig.ACKS_CONFIG, config.get("acks").asText())
        .put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, config.get("enable_idempotence").asBoolean())
        .put(ProducerConfig.COMPRESSION_TYPE_CONFIG, config.get("compression_type").asText())
        .put(ProducerConfig.BATCH_SIZE_CONFIG, config.get("batch_size").asInt())
        .put(ProducerConfig.LINGER_MS_CONFIG, config.get("linger_ms").asLong())
        .put(ProducerConfig.MAX_IN_FLIGHT_REQUESTS_PER_CONNECTION,
            config.get("max_in_flight_requests_per_connection").asInt())
        .put(ProducerConfig.CLIENT_DNS_LOOKUP_CONFIG, config.get("client_dns_lookup").asText())
        .put(ProducerConfig.BUFFER_MEMORY_CONFIG, config.get("buffer_memory").asLong())
        .put(ProducerConfig.MAX_REQUEST_SIZE_CONFIG, config.get("max_request_size").asInt())
        .put(ProducerConfig.RETRIES_CONFIG, config.get("retries").asInt())
        .put(ProducerConfig.SOCKET_CONNECTION_SETUP_TIMEOUT_MS_CONFIG,
            config.get("socket_connection_setup_timeout_ms").asLong())
        .put(ProducerConfig.SOCKET_CONNECTION_SETUP_TIMEOUT_MAX_MS_CONFIG,
            config.get("socket_connection_setup_timeout_max_ms").asLong())
        .put(ProducerConfig.MAX_BLOCK_MS_CONFIG, config.get("max_block_ms").asInt())
        .put(ProducerConfig.REQUEST_TIMEOUT_MS_CONFIG, config.get("request_timeout_ms").asInt())
        .put(ProducerConfig.DELIVERY_TIMEOUT_MS_CONFIG, config.get("delivery_timeout_ms").asInt())
        .put(ProducerConfig.SEND_BUFFER_CONFIG, config.get("send_buffer_bytes").asInt())
        .put(ProducerConfig.RECEIVE_BUFFER_CONFIG, config.get("receive_buffer_bytes").asInt())
        .put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName())
        .put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, JsonSerializer.class.getName())
        .build();

    final Map<String, Object> filteredProps = props.entrySet().stream()
        .filter(entry -> entry.getValue() != null && !entry.getValue().toString().isBlank())
        .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));

    return new KafkaProducer<>(filteredProps);
  }

  private Map<String, Object> propertiesByProtocol(final JsonNode config) {
    final JsonNode protocolConfig = config.get("protocol");
    LOGGER.info("Kafka protocol config: {}", protocolConfig.toString());
    final KafkaProtocol protocol = KafkaProtocol.valueOf(protocolConfig.get("security_protocol").asText().toUpperCase());
    final ImmutableMap.Builder<String, Object> builder = ImmutableMap.<String, Object>builder()
        .put(CommonClientConfigs.SECURITY_PROTOCOL_CONFIG, protocol.toString());

    switch (protocol) {
      case PLAINTEXT -> {}
      case SASL_SSL, SASL_PLAINTEXT -> {
        builder.put(SaslConfigs.SASL_JAAS_CONFIG, protocolConfig.get("sasl_jaas_config").asText());
        builder.put(SaslConfigs.SASL_MECHANISM, protocolConfig.get("sasl_mechanism").asText());
      }
      default -> throw new RuntimeException("Unexpected Kafka protocol: " + Jsons.serialize(protocol));
    }

    return builder.build();
  }

  public String getTopicPattern() {
    return topicPattern;
  }

  public boolean isSync() {
    return sync;
  }

  public KafkaProducer<String, JsonNode> getProducer() {
    return producer;
  }

}
