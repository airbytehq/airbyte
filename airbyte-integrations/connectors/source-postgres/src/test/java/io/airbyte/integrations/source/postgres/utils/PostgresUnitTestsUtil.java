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
import java.util.Map;

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

}
