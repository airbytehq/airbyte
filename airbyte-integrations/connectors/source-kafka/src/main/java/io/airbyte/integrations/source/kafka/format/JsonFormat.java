/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.kafka.format;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.AbstractIterator;
import com.google.common.collect.Lists;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.SyncMode;
import java.time.Duration;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.regex.Pattern;
import java.util.stream.Collectors;
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.common.TopicPartition;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.apache.kafka.connect.json.JsonDeserializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class JsonFormat extends AbstractFormat {

  private static final Logger LOGGER = LoggerFactory.getLogger(JsonFormat.class);

  private KafkaConsumer<String, JsonNode> consumer;

  public JsonFormat(JsonNode jsonConfig) {
    super(jsonConfig);
  }

  @Override
  protected KafkaConsumer<String, JsonNode> getConsumer() {
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
  protected Map<String, Object> getKafkaConfig() {
    Map<String, Object> props = super.getKafkaConfig();
    props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
    props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, JsonDeserializer.class.getName());
    return props;
  }

  public Set<String> getTopicsToSubscribe() {
    if (topicsToSubscribe == null) {
      getConsumer();
    }
    return topicsToSubscribe;
  }

  @Override
  public List<AirbyteStream> getStreams() {
    final Set<String> topicsToSubscribe = getTopicsToSubscribe();
    final List<AirbyteStream> streams = topicsToSubscribe.stream().map(topic -> CatalogHelpers
        .createAirbyteStream(topic, Field.of("value", JsonSchemaType.STRING))
        .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)))
        .collect(Collectors.toList());
    return streams;
  }

  @Override
  public AutoCloseableIterator<AirbyteMessage> read() {

    final KafkaConsumer<String, JsonNode> consumer = getConsumer();
    final List<ConsumerRecord<String, JsonNode>> recordsList = new ArrayList<>();
    final int retry = config.has("repeated_calls") ? config.get("repeated_calls").intValue() : 0;
    final int polling_time = config.has("polling_time") ? config.get("polling_time").intValue() : 100;
    final int max_records = config.has("max_records_process") ? config.get("max_records_process").intValue() : 100000;
    AtomicInteger record_count = new AtomicInteger();
    final Map<String, Integer> poll_lookup = new HashMap<>();
    getTopicsToSubscribe().forEach(topic -> poll_lookup.put(topic, 0));
    while (true) {
      final ConsumerRecords<String, JsonNode> consumerRecords = consumer.poll(Duration.of(polling_time, ChronoUnit.MILLIS));
      consumerRecords.forEach(record -> {
        record_count.getAndIncrement();
        recordsList.add(record);
      });
      consumer.commitAsync();

      if (consumerRecords.count() == 0) {
        consumer.assignment().stream().map(record -> record.topic()).distinct().forEach(
            topic -> {
              poll_lookup.put(topic, poll_lookup.get(topic) + 1);
            });
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
    final Iterator<ConsumerRecord<String, JsonNode>> iterator = recordsList.iterator();
    return AutoCloseableIterators.fromIterator(new AbstractIterator<>() {

      @Override
      protected AirbyteMessage computeNext() {
        if (iterator.hasNext()) {
          final ConsumerRecord<String, JsonNode> record = iterator.next();
          return new AirbyteMessage()
              .withType(AirbyteMessage.Type.RECORD)
              .withRecord(new AirbyteRecordMessage()
                  .withStream(record.topic())
                  .withEmittedAt(Instant.now().toEpochMilli())
                  .withData(record.value()));
        }

        return endOfData();
      }

    });
  }

  @Override
  public boolean isAccessible() {
    try {
      final String testTopic = config.has("test_topic") ? config.get("test_topic").asText() : "";
      if (!testTopic.isBlank()) {
        final KafkaConsumer<String, JsonNode> consumer = getConsumer();
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

}
