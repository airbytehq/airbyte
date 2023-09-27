/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.kafka.converter;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.time.Instant;

public class JsonConverter implements Converter<JsonNode> {

  @Override
  public AirbyteRecordMessage convertToAirbyteRecord(String topic, JsonNode value) {
    return new AirbyteRecordMessage()
        .withStream(topic)
        .withEmittedAt(Instant.now().toEpochMilli())
        .withData(value);
  }
}
