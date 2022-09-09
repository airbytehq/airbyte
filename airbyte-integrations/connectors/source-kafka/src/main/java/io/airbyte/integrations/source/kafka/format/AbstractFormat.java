/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.kafka.format;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.kafka.KafkaProtocol;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;
import org.apache.kafka.clients.CommonClientConfigs;
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.common.config.SaslConfigs;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class AbstractFormat implements KafkaFormat {

  private static final Logger LOGGER = LoggerFactory.getLogger(AbstractFormat.class);

  protected Set<String> topicsToSubscribe;
  protected JsonNode config;

  public AbstractFormat(JsonNode config) {
    this.config = config;

  }

  protected abstract KafkaConsumer<String, ?> getConsumer();

  protected abstract Set<String> getTopicsToSubscribe();

  protected Map<String, Object> getKafkaConfig() {

    final Map<String, Object> props = new HashMap<>();
    props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, config.get("bootstrap_servers").asText());
    props.put(ConsumerConfig.GROUP_ID_CONFIG,
        config.has("group_id") ? config.get("group_id").asText() : null);
    props.put(ConsumerConfig.MAX_POLL_RECORDS_CONFIG,
        config.has("max_poll_records") ? config.get("max_poll_records").intValue() : null);
    props.putAll(propertiesByProtocol(config));
    props.put(ConsumerConfig.CLIENT_ID_CONFIG,
        config.has("client_id") ? config.get("client_id").asText() : null);
    props.put(ConsumerConfig.CLIENT_DNS_LOOKUP_CONFIG, config.get("client_dns_lookup").asText());
    props.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, config.get("enable_auto_commit").booleanValue());
    props.put(ConsumerConfig.AUTO_COMMIT_INTERVAL_MS_CONFIG,
        config.has("auto_commit_interval_ms") ? config.get("auto_commit_interval_ms").intValue() : null);
    props.put(ConsumerConfig.RETRY_BACKOFF_MS_CONFIG,
        config.has("retry_backoff_ms") ? config.get("retry_backoff_ms").intValue() : null);
    props.put(ConsumerConfig.REQUEST_TIMEOUT_MS_CONFIG,
        config.has("request_timeout_ms") ? config.get("request_timeout_ms").intValue() : null);
    props.put(ConsumerConfig.RECEIVE_BUFFER_CONFIG,
        config.has("receive_buffer_bytes") ? config.get("receive_buffer_bytes").intValue() : null);
    props.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG,
        config.has("auto_offset_reset") ? config.get("auto_offset_reset").asText() : null);

    final Map<String, Object> filteredProps = props.entrySet().stream()
        .filter(entry -> entry.getValue() != null && !entry.getValue().toString().isBlank())
        .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));

    return filteredProps;

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

}
