package io.airbyte.integrations.source.kafka;

import io.airbyte.protocol.models.v0.AirbyteRecordMessage;

public record KafkaMessage(String topic, int partition, long offset, AirbyteRecordMessage message) {

}
