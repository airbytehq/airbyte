/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.AirbyteErrorTraceMessage;
import io.airbyte.protocol.models.AirbyteGlobalState;
import io.airbyte.protocol.models.AirbyteLogMessage;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.AirbyteStreamState;
import io.airbyte.protocol.models.AirbyteTraceMessage;
import io.airbyte.protocol.models.StreamDescriptor;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
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

  public static AirbyteMessage createRecordMessage(final String streamName, final int recordData) {
    return new AirbyteMessage()
        .withType(AirbyteMessage.Type.RECORD)
        .withRecord(new AirbyteRecordMessage().withStream(streamName).withData(Jsons.jsonNode(recordData)));
  }

  public static AirbyteMessage createStateMessage(final int stateData) {
    return new AirbyteMessage()
        .withType(AirbyteMessage.Type.STATE)
        .withState(new AirbyteStateMessage().withData(Jsons.jsonNode(stateData)));
  }

  public static AirbyteMessage createStateMessage(final String key, final String value) {
    return new AirbyteMessage()
        .withType(Type.STATE)
        .withState(new AirbyteStateMessage().withData(Jsons.jsonNode(ImmutableMap.of(key, value))));
  }

  public static AirbyteStateMessage createStreamStateMessage(final String streamName, final int stateData) {
    return new AirbyteStateMessage()
        .withType(AirbyteStateType.STREAM)
        .withStream(createStreamState(streamName).withStreamState(Jsons.jsonNode(stateData)));
  }

  public static AirbyteMessage createGlobalStateMessage(final int stateData, final String... streamNames) {
    final List<AirbyteStreamState> streamStates = new ArrayList<>();
    for (final String streamName : streamNames) {
      streamStates.add(createStreamState(streamName).withStreamState(Jsons.jsonNode(stateData)));
    }
    return new AirbyteMessage()
        .withType(Type.STATE)
        .withState(new AirbyteStateMessage().withType(AirbyteStateType.GLOBAL).withGlobal(new AirbyteGlobalState().withStreamStates(streamStates)));
  }

  public static AirbyteStreamState createStreamState(final String streamName) {
    return new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName(streamName));
  }

  public static AirbyteTraceMessage createErrorTraceMessage(final String message, final Double emittedAt) {
    return new AirbyteTraceMessage()
        .withType(io.airbyte.protocol.models.AirbyteTraceMessage.Type.ERROR)
        .withEmittedAt(emittedAt)
        .withError(new AirbyteErrorTraceMessage().withMessage(message));
  }

  public static AirbyteTraceMessage createErrorTraceMessage(final String message,
                                                            final Double emittedAt,
                                                            final AirbyteErrorTraceMessage.FailureType failureType) {
    return new AirbyteTraceMessage()
        .withType(io.airbyte.protocol.models.AirbyteTraceMessage.Type.ERROR)
        .withEmittedAt(emittedAt)
        .withError(new AirbyteErrorTraceMessage().withMessage(message).withFailureType(failureType));
  }

  public static AirbyteMessage createTraceMessage(final String message, final Double emittedAt) {
    return new AirbyteMessage()
        .withType(AirbyteMessage.Type.TRACE)
        .withTrace(new AirbyteTraceMessage()
            .withType(AirbyteTraceMessage.Type.ERROR)
            .withEmittedAt(emittedAt)
            .withError(new AirbyteErrorTraceMessage().withMessage(message)));
  }

}
