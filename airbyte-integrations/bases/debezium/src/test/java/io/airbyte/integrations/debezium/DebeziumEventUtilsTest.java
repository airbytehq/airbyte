/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.debezium.internals.DebeziumEventUtils;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.debezium.engine.ChangeEvent;
import java.io.IOException;
import java.time.Instant;
import org.junit.jupiter.api.Test;

class DebeziumEventUtilsTest {

  @Test
  public void testConvertChangeEvent() throws IOException {
    final String stream = "names";
    final Instant emittedAt = Instant.now();
    final CdcMetadataInjector cdcMetadataInjector = new DummyMetadataInjector();
    ChangeEvent<String, String> insertChangeEvent = mockChangeEvent("insert_change_event.json");
    ChangeEvent<String, String> updateChangeEvent = mockChangeEvent("update_change_event.json");
    ChangeEvent<String, String> deleteChangeEvent = mockChangeEvent("delete_change_event.json");

    final AirbyteMessage actualInsert = DebeziumEventUtils.toAirbyteMessage(insertChangeEvent, cdcMetadataInjector, emittedAt);
    final AirbyteMessage actualUpdate = DebeziumEventUtils.toAirbyteMessage(updateChangeEvent, cdcMetadataInjector, emittedAt);
    final AirbyteMessage actualDelete = DebeziumEventUtils.toAirbyteMessage(deleteChangeEvent, cdcMetadataInjector, emittedAt);

    final AirbyteMessage expectedInsert = createAirbyteMessage(stream, emittedAt, "insert_message.json");
    final AirbyteMessage expectedUpdate = createAirbyteMessage(stream, emittedAt, "update_message.json");
    final AirbyteMessage expectedDelete = createAirbyteMessage(stream, emittedAt, "delete_message.json");

    deepCompare(expectedInsert, actualInsert);
    deepCompare(expectedUpdate, actualUpdate);
    deepCompare(expectedDelete, actualDelete);
  }

  private static ChangeEvent<String, String> mockChangeEvent(String resourceName) throws IOException {
    final ChangeEvent<String, String> mocked = mock(ChangeEvent.class);
    final String resource = MoreResources.readResource(resourceName);
    when(mocked.value()).thenReturn(resource);

    return mocked;
  }

  private static AirbyteMessage createAirbyteMessage(String stream, Instant emittedAt, String resourceName) throws IOException {
    final String data = MoreResources.readResource(resourceName);

    final AirbyteRecordMessage recordMessage = new AirbyteRecordMessage()
        .withStream(stream)
        .withNamespace("public")
        .withData(Jsons.deserialize(data))
        .withEmittedAt(emittedAt.toEpochMilli());

    return new AirbyteMessage()
        .withType(AirbyteMessage.Type.RECORD)
        .withRecord(recordMessage);
  }

  private static void deepCompare(Object expected, Object actual) {
    assertEquals(Jsons.deserialize(Jsons.serialize(expected)), Jsons.deserialize(Jsons.serialize(actual)));
  }

  public static class DummyMetadataInjector implements CdcMetadataInjector {

    @Override
    public void addMetaData(ObjectNode event, JsonNode source) {
      long lsn = source.get("lsn").asLong();
      event.put("_ab_cdc_lsn", lsn);
    }

    @Override
    public String namespace(JsonNode source) {
      return source.get("schema").asText();
    }

  }

}
