/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.protocols.airbyte;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.AirbyteLogMessage;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStateMessage;
import java.time.Instant;
import java.util.Map;

public class AirbyteMessageUtils {

  public static AirbyteMessage createRecordMessage(final String tableName,
                                                   final JsonNode record,
                                                   final Instant timeExtracted) {

    return new AirbyteMessage()
        .withType(AirbyteMessage.Type.RECORD)
        .withRecord(new AirbyteRecordMessage()
            .withData(record)
            .withStream(tableName)
            .withEmittedAt(timeExtracted.getEpochSecond()));
  }

  public static AirbyteMessage createLogMessage(final AirbyteLogMessage.Level level,
                                                final String message) {

    return new AirbyteMessage()
        .withType(AirbyteMessage.Type.LOG)
        .withLog(new AirbyteLogMessage()
            .withLevel(level)
            .withMessage(message));
  }

  public static AirbyteMessage createRecordMessage(final String tableName,
                                                   final String key,
                                                   final String value) {
    return createRecordMessage(tableName, ImmutableMap.of(key, value));
  }

  public static AirbyteMessage createRecordMessage(final String tableName,
                                                   final String key,
                                                   final Integer value) {
    return createRecordMessage(tableName, ImmutableMap.of(key, value));
  }

  public static AirbyteMessage createRecordMessage(final String tableName,
                                                   final Map<String, ?> record) {
    return createRecordMessage(tableName, Jsons.jsonNode(record), Instant.EPOCH);
  }

  public static AirbyteMessage createStateMessage(final String key, final String value) {
    return new AirbyteMessage()
        .withType(Type.STATE)
        .withState(new AirbyteStateMessage().withData(Jsons.jsonNode(ImmutableMap.of(key, value))));
  }

}
