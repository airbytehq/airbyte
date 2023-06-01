package io.airbyte.integrations.source.kafka.mediator;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.source.kafka.KafkaStrategy;
import io.confluent.kafka.schemaregistry.client.SchemaRegistryClientConfig;
import io.confluent.kafka.serializers.KafkaAvroDeserializer;
import io.confluent.kafka.serializers.KafkaAvroDeserializerConfig;
import io.confluent.kafka.serializers.KafkaAvroSerializerConfig;
import java.util.Arrays;
import java.util.List;
import java.util.regex.Pattern;
import java.util.stream.Collectors;
import org.apache.avro.generic.GenericRecord;
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.common.TopicPartition;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class AvroKafkaMediator extends AbstractKafkaMediator<GenericRecord> {

  private static final Logger LOGGER = LoggerFactory.getLogger(AvroKafkaMediator.class);

  public AvroKafkaMediator(JsonNode config) {
    super(config);
    var props = getKafkaConfig();

    props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
    props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, KafkaAvroDeserializer.class.getName());
    props.put(SchemaRegistryClientConfig.BASIC_AUTH_CREDENTIALS_SOURCE, "USER_INFO");
    final JsonNode avroConfig = config.get("MessageFormat");
    props.put(SchemaRegistryClientConfig.USER_INFO_CONFIG,
        String.format("%s:%s", avroConfig.get("schema_registry_username").asText(), avroConfig.get("schema_registry_password").asText()));
    props.put(KafkaAvroDeserializerConfig.SCHEMA_REGISTRY_URL_CONFIG, avroConfig.get("schema_registry_url").asText());
    props.put(KafkaAvroSerializerConfig.VALUE_SUBJECT_NAME_STRATEGY,
        KafkaStrategy.getStrategyName(avroConfig.get("deserialization_strategy").asText()));

    this.consumer = new KafkaConsumer<>(props);

    final JsonNode subscription = config.get("subscription");
    LOGGER.info("Kafka subscribe method: {}", subscription.toString());
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
        LOGGER.info("Topic-partition list: {}", topicPartitionList);
        consumer.assign(topicPartitionList);
      }
    }
  }
}
