/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
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
