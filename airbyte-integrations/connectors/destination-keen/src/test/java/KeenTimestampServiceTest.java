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

package io.airbyte.integrations.destination.keen;

import static java.util.Map.entry;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

public class KeenTimestampServiceTest {

  private final ObjectMapper objectMapper = new ObjectMapper();

  @Test
  void shouldInitializeCursorFieldsFromCatalog() throws IOException {
    ConfiguredAirbyteCatalog configuredCatalog = readConfiguredCatalogFromFile("cursors_catalog.json");

    Map<String, List<String>> expectedCursorFieldsMap = Map.ofEntries(
        entry("StringTypeStream1", List.of("property1")),
        entry("StringTypeStream2", List.of("property1")),
        entry("StringTypeStream3", List.of("property1")),
        entry("NumberTypeStream1", List.of("property1")),
        entry("NumberTypeStream2", List.of("property1")),
        entry("ArrayTypeStream1", List.of("property1")),
        entry("ArrayTypeStream2", List.of("property1")),
        entry("ArrayTypeStream3", List.of("property1")),
        entry("NestedCursorStream", List.of("property1", "inside")));

    KeenTimestampService keenTimestampService = new KeenTimestampService(configuredCatalog, true);

    Map<String, List<String>> cursorFieldMap = keenTimestampService.getStreamCursorFields();
    Assertions.assertEquals(expectedCursorFieldsMap, cursorFieldMap);
  }

  @Test
  void shouldInjectTimestampWhenCursorIsValidString() throws IOException {
    ConfiguredAirbyteCatalog configuredCatalog = readConfiguredCatalogFromFile("string_cursor_catalog.json");

    KeenTimestampService keenTimestampService = new KeenTimestampService(configuredCatalog, true);

    AirbyteMessage message = buildMessageWithCursorValue(configuredCatalog, "1999/12/15 14:44 utc");
    JsonNode expectedJson = buildExpectedJsonWithTimestamp("\"1999/12/15 14:44 utc\"", "1999-12-15T14:44:00Z");
    JsonNode jsonNode = keenTimestampService.injectTimestamp(message.getRecord());

    Assertions.assertEquals(jsonNode, expectedJson);
  }

  @Test
  void shouldInjectNumberTimestampWhenTimestampIsSeconds() throws IOException {
    ConfiguredAirbyteCatalog configuredCatalog = readConfiguredCatalogFromFile("number_cursor_catalog.json");
    KeenTimestampService keenTimestampService = new KeenTimestampService(configuredCatalog, true);

    int secondsCursor = 1628080068;
    AirbyteMessage message = buildMessageWithCursorValue(configuredCatalog, secondsCursor);
    JsonNode expectedJson = buildExpectedJsonWithTimestamp(secondsCursor, "2021-08-04T12:27:48Z");
    JsonNode jsonNode = keenTimestampService.injectTimestamp(message.getRecord());

    Assertions.assertEquals(jsonNode, expectedJson);
  }

  @Test
  void shouldInjectNumberTimestampWhenTimestampIsMillis() throws IOException {
    ConfiguredAirbyteCatalog configuredCatalog = readConfiguredCatalogFromFile("number_cursor_catalog.json");
    KeenTimestampService keenTimestampService = new KeenTimestampService(configuredCatalog, true);

    long millisCursor = 1628081113151L;
    AirbyteMessage message = buildMessageWithCursorValue(configuredCatalog, millisCursor);
    JsonNode expectedJson = buildExpectedJsonWithTimestamp(millisCursor, "2021-08-04T12:45:13.151Z");
    JsonNode jsonNode = keenTimestampService.injectTimestamp(message.getRecord());

    Assertions.assertEquals(jsonNode, expectedJson);
  }

  @Test
  void shouldInjectEmittedAtWhenCursorNumberValueIsTooLow() throws IOException {
    ConfiguredAirbyteCatalog configuredCatalog = readConfiguredCatalogFromFile("number_cursor_catalog.json");
    KeenTimestampService keenTimestampService = new KeenTimestampService(configuredCatalog, true);

    int notUnixTimestampCursor = 250_000;
    AirbyteMessage message = buildMessageWithCursorValue(configuredCatalog, notUnixTimestampCursor);

    // 2020-10-14T01:09:49.200Z is hardcoded emitted at
    JsonNode expectedJson = buildExpectedJsonWithTimestamp(notUnixTimestampCursor, "2020-10-14T01:09:49.200Z");

    JsonNode jsonNode = keenTimestampService.injectTimestamp(message.getRecord());

    Assertions.assertEquals(jsonNode, expectedJson);
  }

  @Test
  void shouldInjectEmittedAtWhenCursorIsUnparsableAndRemoveFieldFromMap() throws IOException {
    ConfiguredAirbyteCatalog configuredCatalog = readConfiguredCatalogFromFile("string_cursor_catalog.json");

    KeenTimestampService keenTimestampService = new KeenTimestampService(configuredCatalog, true);

    Map<String, List<String>> cursorFieldMap = keenTimestampService.getStreamCursorFields();
    Assertions.assertEquals(cursorFieldMap.size(), 1);

    AirbyteMessage message = buildMessageWithCursorValue(configuredCatalog, "some_text");

    // 2020-10-14T01:09:49.200Z is hardcoded emitted at
    JsonNode expectedJson = buildExpectedJsonWithTimestamp("\"some_text\"", "2020-10-14T01:09:49.200Z");

    JsonNode jsonNode = keenTimestampService.injectTimestamp(message.getRecord());

    Assertions.assertEquals(jsonNode, expectedJson);
    Assertions.assertEquals(cursorFieldMap.size(), 0);
  }

  @Test
  void shouldInjectEmittedAtWhenCursorIsValidAndInferenceIsDisabled() throws IOException {
    ConfiguredAirbyteCatalog configuredCatalog = readConfiguredCatalogFromFile("number_cursor_catalog.json");
    KeenTimestampService keenTimestampService = new KeenTimestampService(configuredCatalog, false);

    int secondsCursor = 1628080068;
    AirbyteMessage message = buildMessageWithCursorValue(configuredCatalog, secondsCursor);

    // 2020-10-14T01:09:49.200Z is hardcoded emitted at
    JsonNode expectedJson = buildExpectedJsonWithTimestamp(secondsCursor, "2020-10-14T01:09:49.200Z");
    JsonNode jsonNode = keenTimestampService.injectTimestamp(message.getRecord());

    Assertions.assertEquals(jsonNode, expectedJson);
  }

  @Test
  void shouldInjectTimestampWhenCursorIsNestedField() throws IOException {
    ConfiguredAirbyteCatalog configuredCatalog = readConfiguredCatalogFromFile("nested_cursor_catalog.json");
    KeenTimestampService keenTimestampService = new KeenTimestampService(configuredCatalog, true);

    int secondsCursor = 1628080068;
    AirbyteMessage message = buildMessageWithCursorValue(configuredCatalog,
        ImmutableMap.builder().put("nestedProperty", secondsCursor).build());

    String nestedJson = String.format("{\"nestedProperty\": %s}", secondsCursor);

    JsonNode expectedJson = buildExpectedJsonWithTimestamp(nestedJson, "2021-08-04T12:27:48Z");
    JsonNode jsonNode = keenTimestampService.injectTimestamp(message.getRecord());

    Assertions.assertEquals(jsonNode, expectedJson);
  }

  private <T> AirbyteMessage buildMessageWithCursorValue(ConfiguredAirbyteCatalog configuredCatalog, T cursorValue) {
    return new AirbyteMessage()
        .withType(AirbyteMessage.Type.RECORD)
        .withRecord(new AirbyteRecordMessage()
            .withStream(configuredCatalog.getStreams().get(0).getStream().getName())
            .withEmittedAt(1602637789200L)
            .withData(Jsons.jsonNode(ImmutableMap.builder()
                .put("cursorProperty", cursorValue)
                .put("otherProperty", "something")
                .build())));
  }

  private <T> JsonNode buildExpectedJsonWithTimestamp(T value, String parsedTimestamp)
      throws JsonProcessingException {
    return objectMapper.readTree(
        String.format(
            "{" +
                "\"cursorProperty\": %s," +
                "\"otherProperty\": \"something\"," +
                "\"keen\" : { \"timestamp\": \"%s\"}" +
                "}",
            value, parsedTimestamp));
  }

  private ConfiguredAirbyteCatalog readConfiguredCatalogFromFile(String fileName)
      throws IOException {
    final AirbyteCatalog catalog = Jsons.deserialize(MoreResources.readResource(fileName), AirbyteCatalog.class);
    return new ConfiguredAirbyteCatalog()
        .withStreams(catalog.getStreams()
            .stream()
            .map(this::toConfiguredStreamWithCursors)
            .collect(Collectors.toList()));
  }

  public ConfiguredAirbyteStream toConfiguredStreamWithCursors(AirbyteStream stream) {
    return new ConfiguredAirbyteStream()
        .withStream(stream)
        .withCursorField(stream.getDefaultCursorField());
  }

}
