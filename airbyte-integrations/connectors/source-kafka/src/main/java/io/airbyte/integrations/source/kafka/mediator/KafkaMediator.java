/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.kafka.mediator;

import io.airbyte.integrations.source.kafka.KafkaMessage;
import java.util.List;
import java.util.Map;
import java.util.Set;
import org.apache.kafka.common.TopicPartition;

public interface KafkaMediator {

  List<KafkaMessage> poll();

  Map<TopicPartition, Long> position(Set<TopicPartition> partitions);

}
