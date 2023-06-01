package io.airbyte.integrations.source.kafka.converter;

import io.airbyte.protocol.models.v0.AirbyteMessage;

public interface Converter<V> {

  AirbyteMessage convertToAirbyteRecord(String topic, V value);
}
