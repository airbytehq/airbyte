package io.airbyte.integrations.source.kafka.config;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.kafka.KafkaProtocol;
import io.airbyte.integrations.source.kafka.KafkaStrategy;
import io.airbyte.integrations.source.kafka.MessageFormat;
import io.confluent.kafka.schemaregistry.client.SchemaRegistryClientConfig;
import io.confluent.kafka.serializers.KafkaAvroDeserializer;
import io.confluent.kafka.serializers.KafkaAvroDeserializerConfig;
import io.confluent.kafka.serializers.KafkaAvroSerializerConfig;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;
import org.apache.kafka.clients.CommonClientConfigs;
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.common.config.SaslConfigs;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.apache.kafka.connect.json.JsonDeserializer;

public class ConfigHelper {

  public static SourceConfig fromJson(JsonNode config) {
    final var messageFormat = MessageFormat.valueOf(
        Optional.ofNullable(config.get("MessageFormat")).map(it -> it.get("deserialization_type").asText().toUpperCase()).orElse("JSON")
    );
    final var maxRecords = config.has("max_records_process") ? config.get("max_records_process").intValue() : 100000;
    final var maxRetries = config.has("repeated_calls") ? config.get("repeated_calls").intValue() : 0;
    final var pollingTimeInMs = config.has("polling_time") ? config.get("polling_time").intValue() : 100;
    final var kafkaConfig = new KafkaConfig(getKafkaConfigByFormat(config, messageFormat), getKafkaSubscriptionConfig(config));
    return new SourceConfig(messageFormat, kafkaConfig, maxRecords, maxRetries, pollingTimeInMs);
  }

  private static Map<String, Object> getKafkaConfigByFormat(JsonNode config, MessageFormat format) {
    Map<String, Object> props = getKafkaProperties(config);

    switch (format) {
      case AVRO -> {
        props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, KafkaAvroDeserializer.class.getName());
        props.put(SchemaRegistryClientConfig.BASIC_AUTH_CREDENTIALS_SOURCE, "USER_INFO");
        final JsonNode avroConfig = config.get("MessageFormat");
        props.put(SchemaRegistryClientConfig.USER_INFO_CONFIG,
            String.format("%s:%s", avroConfig.get("schema_registry_username").asText(), avroConfig.get("schema_registry_password").asText()));
        props.put(KafkaAvroDeserializerConfig.SCHEMA_REGISTRY_URL_CONFIG, avroConfig.get("schema_registry_url").asText());
        props.put(KafkaAvroSerializerConfig.VALUE_SUBJECT_NAME_STRATEGY,
            KafkaStrategy.getStrategyName(avroConfig.get("deserialization_strategy").asText()));
      }
      case JSON -> {
        props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, JsonDeserializer.class.getName());
      }
    }

    return props;
  }

  private static Map<String, Object> getKafkaProperties(JsonNode config) {
    final Map<String, Object> props = new HashMap<>();
    props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, config.get("bootstrap_servers").asText());
    props.put(ConsumerConfig.GROUP_ID_CONFIG,
        config.has("group_id") ? config.get("group_id").asText() : null);
    props.put(ConsumerConfig.MAX_POLL_RECORDS_CONFIG,
        config.has("max_poll_records") ? config.get("max_poll_records").intValue() : null);
    props.putAll(getSecurityProtocolConfig(config));
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

    return props.entrySet().stream()
        .filter(entry -> entry.getValue() != null && !entry.getValue().toString().isBlank())
        .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));
  }

  private static Map<String, String> getKafkaSubscriptionConfig(JsonNode config) {
    final Map<String, String> props = new HashMap<>();
    final var subscription = config.get("subscription");

    props.put("subscription_type", subscription.get("subscription_type").asText());

    if (subscription.get("topic_pattern") != null) {
      props.put("topic_pattern", subscription.get("topic_pattern").asText());
    }

    if (subscription.get("topic_partitions") != null) {
      props.put("topic_partitions", subscription.get("topic_partitions").asText());
    }

    return props;
  }

  private static Map<String, Object> getSecurityProtocolConfig(final JsonNode config) {
    final JsonNode protocolConfig = config.get("protocol");
    final KafkaProtocol protocol = KafkaProtocol.valueOf(protocolConfig.get("security_protocol").asText().toUpperCase());
    final Map<String, Object> props = new HashMap<>();

    props.put(CommonClientConfigs.SECURITY_PROTOCOL_CONFIG, protocol.toString());

    switch (protocol) {
      case PLAINTEXT -> {
      }
      case SASL_SSL, SASL_PLAINTEXT -> {
        props.put(SaslConfigs.SASL_JAAS_CONFIG, protocolConfig.get("sasl_jaas_config").asText());
        props.put(SaslConfigs.SASL_MECHANISM, protocolConfig.get("sasl_mechanism").asText());
      }
      default -> throw new RuntimeException("Unexpected Kafka protocol: " + Jsons.serialize(protocol));
    }

    return props;
  }

}
