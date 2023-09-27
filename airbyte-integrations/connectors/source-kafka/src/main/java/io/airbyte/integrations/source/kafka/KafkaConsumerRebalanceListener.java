/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.kafka;

import java.util.Collection;
import java.util.Map;
import java.util.Optional;
import org.apache.kafka.clients.consumer.ConsumerRebalanceListener;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.common.TopicPartition;

public class KafkaConsumerRebalanceListener implements ConsumerRebalanceListener {

  public KafkaConsumerRebalanceListener(final KafkaConsumer<?, ?> consumer, final Map<TopicPartition, Long> positions) {
    this.consumer = consumer;
    this.positions = positions;
  }

  @Override
  public void onPartitionsRevoked(final Collection<TopicPartition> partitions) {

  }

  @Override
  public void onPartitionsAssigned(final Collection<TopicPartition> partitions) {
    partitions.forEach(partition -> Optional.ofNullable(positions.get(partition)).ifPresent(position -> consumer.seek(partition, position)));
  }

  private final KafkaConsumer<?, ?> consumer;
  private final Map<TopicPartition, Long> positions;
}
