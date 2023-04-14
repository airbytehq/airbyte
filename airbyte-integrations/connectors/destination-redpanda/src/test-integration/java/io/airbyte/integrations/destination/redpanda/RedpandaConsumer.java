/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redpanda;

import java.util.Map;
import org.apache.kafka.clients.consumer.KafkaConsumer;

public class RedpandaConsumer<K, V> extends KafkaConsumer<K, V> {

  public RedpandaConsumer(Map<String, Object> configs) {
    super(configs);
  }

}
