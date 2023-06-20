/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.kafka.mediator;

import io.airbyte.integrations.source.kafka.KafkaConsumerRebalanceListener;
import io.airbyte.integrations.source.kafka.KafkaMessage;
import io.airbyte.integrations.source.kafka.converter.Converter;
import java.time.Duration;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Optional;
import java.util.Set;
import java.util.regex.Pattern;
import java.util.stream.Collectors;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.common.TopicPartition;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DefaultKafkaMediator<V> implements KafkaMediator {

  private final KafkaConsumer<String, V> consumer;
  private final Converter<V> converter;
  private final int pollingTimeInMs;

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultKafkaMediator.class);

  public DefaultKafkaMediator(KafkaConsumer<String, V> consumer, Converter<V> converter, int pollingTimeInMs,
      Map<String, String> subscription, Map<TopicPartition, Long> initialOffsets) {
    final KafkaConsumerRebalanceListener listener = new KafkaConsumerRebalanceListener(consumer, initialOffsets);
    LOGGER.info("Kafka subscribe method: {}", subscription.toString());
    switch (subscription.get("subscription_type")) {
      case "subscribe" -> {
        final String topicPattern = subscription.get("topic_pattern");
        consumer.subscribe(Pattern.compile(topicPattern), listener);
      }
      case "assign" -> {
        final String topicPartitions = subscription.get("topic_partitions");
        final String[] topicPartitionsStr = topicPartitions.replaceAll("\\s+", "").split(",");
        final List<TopicPartition> topicPartitionList = Arrays.stream(topicPartitionsStr).map(topicPartition -> {
          final String[] pair = topicPartition.split(":");
          return new TopicPartition(pair[0], Integer.parseInt(pair[1]));
        }).collect(Collectors.toList());
        LOGGER.info("Topic-partition list: {}", topicPartitionList);
        consumer.assign(topicPartitionList);
        topicPartitionList.forEach(partition -> Optional.ofNullable(initialOffsets.get(partition))
            .ifPresent(offset -> consumer.seek(partition, offset)));
      }
    }

    this.consumer = consumer;
    this.converter = converter;
    this.pollingTimeInMs = pollingTimeInMs;
  }

  @Override
  public List<KafkaMessage> poll() {
    List<KafkaMessage> output = new ArrayList<>();
    consumer.poll(Duration.of(this.pollingTimeInMs, ChronoUnit.MILLIS)).forEach(it -> {
      final var message = new KafkaMessage(it.topic(), it.partition(), it.offset(), this.converter.convertToAirbyteRecord(it.topic(), it.value()));
      output.add(message);
    });
    return output;
  }

  @Override
  public Map<TopicPartition, Long> position(Set<TopicPartition> partitions) {
    return partitions.stream()
        .map(it -> Map.entry(it, consumer.position(it)))
        .collect(Collectors.toMap(Entry::getKey, Entry::getValue));
  }

}
