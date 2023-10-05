/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.kafka.format;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.AbstractIterator;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.kafka.KafkaProtocol;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

import io.airbyte.protocol.models.v0.AirbyteMessage;
import org.apache.kafka.clients.CommonClientConfigs;
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.common.config.SaslConfigs;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class AbstractFormat extends AbstractIterator<AirbyteMessage> implements KafkaFormat {
  private static final Logger LOGGER = LoggerFactory.getLogger(AbstractFormat.class);
  protected Set<String> topicsToSubscribe;
  protected JsonNode config;

  public AbstractFormat(JsonNode config) {
    this.config = config;
    this.iskafkaCheckpoint = config.has("enable_kafka_checkpoint") ? config.get("enable_kafka_checkpoint").booleanValue() : true;
  }

  protected abstract KafkaConsumer<String, ?> getConsumer();

  protected abstract Set<String> getTopicsToSubscribe();

  private boolean iskafkaCheckpoint;

  protected Map<String, Object> getKafkaConfig() {
    Map<String, Object> props = new HashMap();
    props.put("bootstrap.servers", this.config.get("bootstrap_servers").asText());
    props.put("group.id", this.config.has("group_id") ? this.config.get("group_id").asText() : null);
    props.put("max.poll.records", this.config.has("max_poll_records") ? this.config.get("max_poll_records").intValue() : null);
    props.putAll(this.propertiesByProtocol(this.config));
    props.put("client.id", this.config.has("client_id") ? this.config.get("client_id").asText() : null);
    props.put("client.dns.lookup", this.config.get("client_dns_lookup").asText());
    props.put("enable.auto.commit", this.config.get("enable_auto_commit").booleanValue());
    props.put("auto.commit.interval.ms", this.config.has("auto_commit_interval_ms") ? this.config.get("auto_commit_interval_ms").intValue() : null);
    props.put("retry.backoff.ms", this.config.has("retry_backoff_ms") ? this.config.get("retry_backoff_ms").intValue() : null);
    props.put("request.timeout.ms", this.config.has("request_timeout_ms") ? this.config.get("request_timeout_ms").intValue() : null);
    props.put("receive.buffer.bytes", this.config.has("receive_buffer_bytes") ? this.config.get("receive_buffer_bytes").intValue() : null);
    props.put("auto.offset.reset", this.config.has("auto_offset_reset") ? this.config.get("auto_offset_reset").asText() : null);
    Map<String, Object> filteredProps = (Map)props.entrySet().stream().filter((entry) -> {
      return entry.getValue() != null && !entry.getValue().toString().isBlank();
    }).collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));
    return filteredProps;
  }

  private Map<String, Object> propertiesByProtocol(JsonNode config) {
    JsonNode protocolConfig = config.get("protocol");
    LOGGER.info("Kafka protocol config: {}", protocolConfig.toString());
    final KafkaProtocol protocol = KafkaProtocol.valueOf(protocolConfig.get("security_protocol").asText().toUpperCase());
    final ImmutableMap.Builder<String, Object> builder = ImmutableMap.<String, Object>builder()
        .put(CommonClientConfigs.SECURITY_PROTOCOL_CONFIG, protocol.toString());

    switch (protocol) {
      case SASL_SSL:
      case SASL_PLAINTEXT:
        builder.put("sasl.jaas.config", protocolConfig.get("sasl_jaas_config").asText());
        builder.put("sasl.mechanism", protocolConfig.get("sasl_mechanism").asText());
      case PLAINTEXT:
        return builder.build();
      default:
        throw new RuntimeException("Unexpected Kafka protocol: " + Jsons.serialize(protocol));
    }
  }

  protected Map<String, JsonNode> convertToMap(JsonNode root) {
    Map<String, JsonNode> properties = new HashMap();
    if (root.isObject()) {
      Set<String> keys = Jsons.keys(root);
      Iterator var4 = keys.iterator();

      while(var4.hasNext()) {
        String key = (String)var4.next();
        JsonNode property = root.get(key);
        properties.put(key, property);
      }
    }
    return properties;
  }

  protected Map<Integer, Long> extractOffset(JsonNode root) {
    Map<Integer, Long> properties = new HashMap();
    if (root.isObject()) {
      Set<String> keys = Jsons.keys(root);
      Iterator var4 = keys.iterator();
      while(var4.hasNext()) {
        String key = (String)var4.next();
        JsonNode property = root.get(key);
        properties.put(Integer.parseInt(key), property.asLong());
      }
    }

    return properties;
  }

  @Override
  public boolean iskafkaCheckpoint() {
    return iskafkaCheckpoint;
  }
}