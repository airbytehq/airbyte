package io.airbyte.integrations.source.kafka.consumer;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.kafka.KafkaProtocol;
import io.airbyte.integrations.source.kafka.KafkaStrategy;
import io.confluent.kafka.schemaregistry.client.SchemaRegistryClientConfig;
import io.confluent.kafka.serializers.KafkaAvroDeserializer;
import io.confluent.kafka.serializers.KafkaAvroDeserializerConfig;
import io.confluent.kafka.serializers.KafkaAvroSerializerConfig;
import org.apache.avro.generic.GenericRecord;
import org.apache.commons.lang3.NotImplementedException;
import org.apache.kafka.clients.CommonClientConfigs;
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.common.TopicPartition;
import org.apache.kafka.common.config.SaslConfigs;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.apache.kafka.connect.json.JsonDeserializer;

import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

// This can be substituted with a Consumer Abstract class and a Json and
// Avro specific subclasses in case we want other information from the
// consumer
// TODO we can wrap the the subscription part and the retrieval of
// TODO the props into a generic functions that takes in input a lambda

/**
 * allows to create the consumer for AVRO and JSON events
 */
public class ConsumerManager {

    public static KafkaConsumer<String, JsonNode> getJsonConsumer(JsonNode config) {
        Map<String, Object> props = getProps(config);

        props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, JsonDeserializer.class.getName());

        KafkaConsumer<String, JsonNode> consumer = new KafkaConsumer<>(props);
        subscribeConsumer(consumer, config);

        return consumer;
    }

    public static KafkaConsumer<String, GenericRecord> getAvroConsumer(JsonNode config) {
        Map<String, Object> props = getProps(config);

        props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, KafkaAvroDeserializer.class.getName());
        props.put(SchemaRegistryClientConfig.BASIC_AUTH_CREDENTIALS_SOURCE, "USER_INFO");
        final JsonNode avroConfig = config.get("MessageFormat");
        props.put(SchemaRegistryClientConfig.USER_INFO_CONFIG,
                String.format("%s:%s", avroConfig.get("schema_registry_username").asText(), avroConfig.get("schema_registry_password").asText()));
        props.put(KafkaAvroDeserializerConfig.SCHEMA_REGISTRY_URL_CONFIG, avroConfig.get("schema_registry_url").asText());
        props.put(KafkaAvroSerializerConfig.VALUE_SUBJECT_NAME_STRATEGY,
                KafkaStrategy.getStrategyName(avroConfig.get("deserialization_strategy").asText()));

        KafkaConsumer<String, GenericRecord> consumer =  new KafkaConsumer<>(props);

        subscribeConsumer(consumer, config);

        return consumer;

    }

    private static void subscribeConsumer(KafkaConsumer<String, ?> consumer, JsonNode config) {
        final JsonNode subscription = config.get("subscription");
        //LOGGER.info("Kafka subscribe method: {}", subscription.toString());
        switch (subscription.get("subscription_type").asText()) {
            case "subscribe" -> {
                final String topicPattern = subscription.get("topic_pattern").asText();
                consumer.subscribe(Pattern.compile(topicPattern));
            }
            case "assign" -> {
                final String topicPartitions = subscription.get("topic_partitions").asText();
                final String[] topicPartitionsStr = topicPartitions.replaceAll("\\s+", "").split(",");
                final List<TopicPartition> topicPartitionList = Arrays.stream(topicPartitionsStr).map(topicPartition -> {
                    final String[] pair = topicPartition.split(":");
                    return new TopicPartition(pair[0], Integer.parseInt(pair[1]));
                }).collect(Collectors.toList());
                //LOGGER.info("Topic-partition list: {}", topicPartitionList);
                consumer.assign(topicPartitionList);
            }
        }
    }

    private static Map<String, Object> getProps(JsonNode config) {
        Map<String, Object> props = new HashMap<>();
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

    private static Map<String, Object> propertiesByProtocol(final JsonNode config) {
        final JsonNode protocolConfig = config.get("protocol");
        // LOGGER.info("Kafka protocol config: {}", protocolConfig.toString());
        final KafkaProtocol protocol = KafkaProtocol.valueOf(protocolConfig.get("security_protocol").asText().toUpperCase());
        final ImmutableMap.Builder<String, Object> builder = ImmutableMap.<String, Object>builder()
                .put(CommonClientConfigs.SECURITY_PROTOCOL_CONFIG, protocol.toString());

        switch (protocol) {
            case PLAINTEXT -> {
            }
            case SASL_SSL, SASL_PLAINTEXT -> {
                builder.put(SaslConfigs.SASL_JAAS_CONFIG, protocolConfig.get("sasl_jaas_config").asText());
                builder.put(SaslConfigs.SASL_MECHANISM, protocolConfig.get("sasl_mechanism").asText());
            }
            default -> throw new RuntimeException("Unexpected Kafka protocol: " + Jsons.serialize(protocol));
        }

        return builder.build();
    }


}
