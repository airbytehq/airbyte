/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.utils;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

public class PostgresUnitTestsUtil {

  public static void setEmittedAtToNull(final Iterable<AirbyteMessage> messages) {
    for (final AirbyteMessage actualMessage : messages) {
      if (actualMessage.getRecord() != null) {
        actualMessage.getRecord().setEmittedAt(null);
      }
    }
  }

  public static AirbyteMessage createRecord(final String stream, final Map<Object, Object> data, String schemaName) {
    return new AirbyteMessage().withType(Type.RECORD)
        .withRecord(new AirbyteRecordMessage().withData(Jsons.jsonNode(data)).withStream(stream).withNamespace(schemaName));
  }

  public static AirbyteMessage createRecord(final String stream, final String namespace, final Map<Object, Object> data) {
    return new AirbyteMessage().withType(Type.RECORD)
        .withRecord(new AirbyteRecordMessage().withData(Jsons.jsonNode(data)).withStream(stream).withNamespace(namespace));
  }

  public static Map<Object, Object> map(final Object... entries) {
    if (entries.length % 2 != 0) {
      throw new IllegalArgumentException("Entries must have even length");
    }

    return new HashMap<>() {

      {
        for (int i = 0; i < entries.length; i++) {
          put(entries[i++], entries[i]);
        }
      }

    };
  }

  public static AirbyteStateMessage generateStateMessage(final String streamName, final String namespace, final JsonNode stateData) {
    return new AirbyteStateMessage()
        .withType(AirbyteStateType.STREAM)
        .withStream(new AirbyteStreamState()
            .withStreamDescriptor(new StreamDescriptor()
                .withName(streamName)
                .withNamespace(namespace))
            .withStreamState(stateData));
  }

  public static List<AirbyteStateMessage> extractStateMessage(final List<AirbyteMessage> messages) {
    return messages.stream().filter(r -> r.getType() == Type.STATE).map(AirbyteMessage::getState)
        .collect(Collectors.toList());
  }

  public static List<AirbyteStateMessage> extractStateMessage(final List<AirbyteMessage> messages, final String streamName) {
    return messages.stream().filter(r -> r.getType() == Type.STATE &&
        r.getState().getStream().getStreamDescriptor().getName().equals(streamName)).map(AirbyteMessage::getState)
        .collect(Collectors.toList());
  }

  public static List<AirbyteMessage> filterRecords(final List<AirbyteMessage> messages) {
    return messages.stream().filter(r -> r.getType() == Type.RECORD)
        .collect(Collectors.toList());
  }

  public static Set<AirbyteMessage> filterRecords(final Set<AirbyteMessage> messages) {
    return messages.stream().filter(r -> r.getType() == Type.RECORD)
        .collect(Collectors.toSet());
  }

  public static List<String> extractSpecificFieldFromCombinedMessages(final List<AirbyteMessage> messages,
                                                                      final String streamName,
                                                                      final String field) {
    return extractStateMessage(messages).stream()
        .filter(s -> s.getStream().getStreamDescriptor().getName().equals(streamName))
        .map(s -> s.getStream().getStreamState().get(field) != null ? s.getStream().getStreamState().get(field).asText() : "").toList();
  }

}
