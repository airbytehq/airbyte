package io.airbyte.integrations.source.kafka.converter;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.time.Instant;

public class JsonConverter implements Converter<JsonNode> {

  @Override
  public AirbyteMessage convertToAirbyteRecord(String topic, JsonNode value) {
    return new AirbyteMessage()
        .withType(AirbyteMessage.Type.RECORD)
        .withRecord(new AirbyteRecordMessage()
            .withStream(topic)
            .withEmittedAt(Instant.now().toEpochMilli())
            .withData(value));

  }
}
