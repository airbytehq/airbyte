/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.kafka;

import io.confluent.kafka.serializers.subject.RecordNameStrategy;
import io.confluent.kafka.serializers.subject.TopicNameStrategy;
import io.confluent.kafka.serializers.subject.TopicRecordNameStrategy;

/**
 * https://docs.confluent.io/platform/current/schema-registry/serdes-develop/index.html
 */
public enum KafkaStrategy {

  TopicNameStrategy(TopicNameStrategy.class.getName()),
  RecordNameStrategy(RecordNameStrategy.class.getName()),
  TopicRecordNameStrategy(TopicRecordNameStrategy.class.getName());

  String className;

  KafkaStrategy(String name) {
    this.className = name;
  }

  public static String getStrategyName(String name) {
    for (KafkaStrategy value : KafkaStrategy.values()) {
      if (value.name().equalsIgnoreCase(name)) {
        return value.className;
      }
    }
    throw new IllegalArgumentException("Unexpected data to strategy setting: " + name);
  }

}
