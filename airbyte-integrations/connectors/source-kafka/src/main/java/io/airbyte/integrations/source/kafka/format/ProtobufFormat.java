/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.kafka.format;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.AbstractIterator;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.integrations.source.kafka.KafkaStrategy;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.SyncMode;
import io.confluent.kafka.schemaregistry.client.SchemaRegistryClientConfig;
import io.confluent.kafka.serializers.protobuf.KafkaProtobufDeserializer;
import io.confluent.kafka.serializers.protobuf.KafkaProtobufDeserializerConfig;
import io.confluent.kafka.serializers.protobuf.KafkaProtobufSerializerConfig;
import java.time.Duration;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.regex.Pattern;
import java.util.stream.Collectors;
import com.google.protobuf.DynamicMessage;
import org.apache.commons.lang3.StringUtils;
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.common.TopicPartition;
import org.apache.kafka.common.security.oauthbearer.OAuthBearerLoginModule;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ProtobufFormat extends AbstractFormat {

  private static final Logger LOGGER = LoggerFactory.getLogger(ProtobufFormat.class);

  private KafkaConsumer<String, DynamicMessage> consumer;

  public ProtobufFormat(JsonNode jsonConfig) {
    super(jsonConfig);
  }

  @Override
  protected Map<String, Object> getKafkaConfig() {
    Map<String, Object> props = super.getKafkaConfig();
    final JsonNode protobuf_config = config.get("MessageFormat");
    props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
    props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, KafkaProtobufDeserializer.class.getName());
    if (protobuf_config.has("schema_registry_username")) {
      props.put(SchemaRegistryClientConfig.BASIC_AUTH_CREDENTIALS_SOURCE, "USER_INFO");
      props.put(SchemaRegistryClientConfig.USER_INFO_CONFIG,
          String.format("%s:%s", protobuf_config.get("schema_registry_username").asText(), protobuf_config.get("schema_registry_password").asText()));
    } else {
      // If the registry username is missing; and the sasl_mechanism == OAUTHBEARER
      final JsonNode protocolConfig = config.get("protocol");
      if (protocolConfig.has("sasl_mechanism") &&
              protocolConfig.get("sasl_mechanism").asText().equals(OAuthBearerLoginModule.OAUTHBEARER_MECHANISM)) {
        props.put(SchemaRegistryClientConfig.BEARER_AUTH_CREDENTIALS_SOURCE, "SASL_OAUTHBEARER_INHERIT");
      }
    }
    props.put(KafkaProtobufDeserializerConfig.SCHEMA_REGISTRY_URL_CONFIG, protobuf_config.get("schema_registry_url").asText());
    props.put(KafkaProtobufSerializerConfig.VALUE_SUBJECT_NAME_STRATEGY,
        KafkaStrategy.getStrategyName(protobuf_config.get("deserialization_strategy").asText()));
    return props;
  }

  @Override
  protected KafkaConsumer<String, DynamicMessage> getConsumer() {
    if (consumer != null) {
      return consumer;
    }
    Map<String, Object> filteredProps = getKafkaConfig();
    consumer = new KafkaConsumer<>(filteredProps);

    final JsonNode subscription = config.get("subscription");
    LOGGER.info("Kafka subscribe method: {}", subscription.toString());
    switch (subscription.get("subscription_type").asText()) {
      case "subscribe" -> {
        final String topicPattern = subscription.get("topic_pattern").asText();
        consumer.subscribe(Pattern.compile(topicPattern));
        topicsToSubscribe = consumer.listTopics().keySet().stream()
            .filter(topic -> topic.matches(topicPattern))
            .collect(Collectors.toSet());
        LOGGER.info("Topic list: {}", topicsToSubscribe);
      }
      case "assign" -> {
        topicsToSubscribe = new HashSet<>();
        final String topicPartitions = subscription.get("topic_partitions").asText();
        final String[] topicPartitionsStr = topicPartitions.replaceAll("\\s+", "").split(",");
        final List<TopicPartition> topicPartitionList = Arrays.stream(topicPartitionsStr).map(topicPartition -> {
          final String[] pair = topicPartition.split(":");
          topicsToSubscribe.add(pair[0]);
          return new TopicPartition(pair[0], Integer.parseInt(pair[1]));
        }).collect(Collectors.toList());
        LOGGER.info("Topic-partition list: {}", topicPartitionList);
        consumer.assign(topicPartitionList);
      }
    }
    return consumer;
  }

  @Override
  protected Set<String> getTopicsToSubscribe() {
    if (topicsToSubscribe == null) {
      getConsumer();
    }
    return topicsToSubscribe;
  }

  @Override
  public boolean isAccessible() {
    try {
      final String testTopic = config.has("test_topic") ? config.get("test_topic").asText() : "";
      if (!testTopic.isBlank()) {
        final KafkaConsumer<String, DynamicMessage> consumer = getConsumer();
        consumer.subscribe(Pattern.compile(testTopic));
        consumer.listTopics();
        consumer.close();
        LOGGER.info("Successfully connected to Kafka brokers for topic '{}'.", config.get("test_topic").asText());
      }
      return true;
    } catch (final Exception e) {
      LOGGER.error("Exception attempting to connect to the Kafka brokers: ", e);
      return false;
    }
  }

  @Override
  public List<AirbyteStream> getStreams() {
    final Set<String> topicsToSubscribe = getTopicsToSubscribe();
      return topicsToSubscribe.stream().map(topic -> CatalogHelpers
          .createAirbyteStream(topic, Field.of("value", JsonSchemaType.STRING))
          .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)))
          .collect(Collectors.toList());
  }

  @Override
  public AutoCloseableIterator<AirbyteMessage> read() {

    final KafkaConsumer<String, DynamicMessage> consumer = getConsumer();
    final List<ConsumerRecord<String, DynamicMessage>> recordsList = new ArrayList<>();
    final int retry = config.has("repeated_calls") ? config.get("repeated_calls").intValue() : 0;
    final int polling_time = config.has("polling_time") ? config.get("polling_time").intValue() : 100;
    final int max_records = config.has("max_records_process") ? config.get("max_records_process").intValue() : 100000;
    AtomicInteger record_count = new AtomicInteger();
    final Map<String, Integer> poll_lookup = new HashMap<>();
    getTopicsToSubscribe().forEach(topic -> poll_lookup.put(topic, 0));
    while (true) {
      final ConsumerRecords<String, DynamicMessage> consumerRecords = consumer.poll(Duration.of(polling_time, ChronoUnit.MILLIS));
      consumerRecords.forEach(record -> {
        record_count.getAndIncrement();
        recordsList.add(record);
      });
      consumer.commitAsync();

      if (consumerRecords.count() == 0) {
        consumer.assignment().stream().map(TopicPartition::topic).distinct().forEach(
            topic -> poll_lookup.put(topic, poll_lookup.get(topic) + 1));
        boolean is_complete = poll_lookup.entrySet().stream().allMatch(
            e -> e.getValue() > retry);
        if (is_complete) {
          LOGGER.info("There is no new data in the queue!!");
          break;
        }
      } else if (record_count.get() > max_records) {
        LOGGER.info("Max record count is reached !!");
        break;
      }
    }
    consumer.close();
    final Iterator<ConsumerRecord<String, DynamicMessage>> iterator = recordsList.iterator();
    return AutoCloseableIterators.fromIterator(new AbstractIterator<>() {

      @Override
      protected AirbyteMessage computeNext() {
        if (iterator.hasNext()) {
          final ConsumerRecord<String, DynamicMessage> record = iterator.next();
          DynamicMessage protobuf_data = record.value();
          ObjectMapper mapper = new ObjectMapper();
          String namespace = protobuf_data.getDescriptorForType().getFile().getPackage();
          String name = protobuf_data.getDescriptorForType().getName();
          JsonNode output;
          try {
            if (StringUtils.isNoneEmpty(namespace) && StringUtils.isNoneEmpty(name)) {
              String newString = String.format("{\"protobuf_schema\": \"%s\",\"name\":\"%s\"}", namespace, name);
              JsonNode newNode = mapper.readTree(newString);
              output = mapper.readTree(protobuf_data.toString());
              ((ObjectNode) output).set("_namespace_", newNode);
            } else {
              output = mapper.readTree(protobuf_data.toString());
            }
          } catch (JsonProcessingException e) {
            LOGGER.error("Exception whilst reading protobuf data from stream", e);
            throw new RuntimeException(e);
          }
          return new AirbyteMessage()
              .withType(AirbyteMessage.Type.RECORD)
              .withRecord(new AirbyteRecordMessage()
                  .withStream(record.topic())
                  .withEmittedAt(Instant.now().toEpochMilli())
                  .withData(Jsons.jsonNode(ImmutableMap.builder().put("value", output).build())));
        }

        return endOfData();
      }

    });
  }

}
