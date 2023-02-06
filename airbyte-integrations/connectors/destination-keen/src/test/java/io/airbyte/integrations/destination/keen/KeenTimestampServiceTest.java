/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.keen;

import static java.util.Map.entry;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
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
    final ConfiguredAirbyteCatalog configuredCatalog = readConfiguredCatalogFromFile("cursors_catalog.json");

    final Map<String, List<String>> expectedCursorFieldsMap = Map.ofEntries(
        entry("StringTypeStream1", List.of("property1")),
        entry("StringTypeStream2", List.of("property1")),
        entry("StringTypeStream3", List.of("property1")),
        entry("NumberTypeStream1", List.of("property1")),
        entry("NumberTypeStream2", List.of("property1")),
        entry("ArrayTypeStream1", List.of("property1")),
        entry("ArrayTypeStream2", List.of("property1")),
        entry("ArrayTypeStream3", List.of("property1")),
        entry("NestedCursorStream", List.of("property1", "inside")));

    final KeenTimestampService keenTimestampService = new KeenTimestampService(configuredCatalog, true);

    final Map<String, List<String>> cursorFieldMap = keenTimestampService.getStreamCursorFields();
    Assertions.assertEquals(expectedCursorFieldsMap, cursorFieldMap);
  }

  @Test
  void shouldInjectTimestampWhenCursorIsValidString() throws IOException {
    final ConfiguredAirbyteCatalog configuredCatalog = readConfiguredCatalogFromFile("string_cursor_catalog.json");

    final KeenTimestampService keenTimestampService = new KeenTimestampService(configuredCatalog, true);

    final AirbyteMessage message = buildMessageWithCursorValue(configuredCatalog, "1999/12/15 14:44 utc");
    final JsonNode expectedJson = buildExpectedJsonWithTimestamp("\"1999/12/15 14:44 utc\"", "1999-12-15T14:44:00Z");
    final JsonNode jsonNode = keenTimestampService.injectTimestamp(message.getRecord());

    Assertions.assertEquals(jsonNode, expectedJson);
  }

  @Test
  void shouldInjectNumberTimestampWhenTimestampIsSeconds() throws IOException {
    final ConfiguredAirbyteCatalog configuredCatalog = readConfiguredCatalogFromFile("number_cursor_catalog.json");
    final KeenTimestampService keenTimestampService = new KeenTimestampService(configuredCatalog, true);

    final int secondsCursor = 1628080068;
    final AirbyteMessage message = buildMessageWithCursorValue(configuredCatalog, secondsCursor);
    final JsonNode expectedJson = buildExpectedJsonWithTimestamp(secondsCursor, "2021-08-04T12:27:48Z");
    final JsonNode jsonNode = keenTimestampService.injectTimestamp(message.getRecord());

    Assertions.assertEquals(jsonNode, expectedJson);
  }

  @Test
  void shouldInjectNumberTimestampWhenTimestampIsMillis() throws IOException {
    final ConfiguredAirbyteCatalog configuredCatalog = readConfiguredCatalogFromFile("number_cursor_catalog.json");
    final KeenTimestampService keenTimestampService = new KeenTimestampService(configuredCatalog, true);

    final long millisCursor = 1628081113151L;
    final AirbyteMessage message = buildMessageWithCursorValue(configuredCatalog, millisCursor);
    final JsonNode expectedJson = buildExpectedJsonWithTimestamp(millisCursor, "2021-08-04T12:45:13.151Z");
    final JsonNode jsonNode = keenTimestampService.injectTimestamp(message.getRecord());

    Assertions.assertEquals(jsonNode, expectedJson);
  }

  @Test
  void shouldInjectEmittedAtWhenCursorNumberValueIsTooLow() throws IOException {
    final ConfiguredAirbyteCatalog configuredCatalog = readConfiguredCatalogFromFile("number_cursor_catalog.json");
    final KeenTimestampService keenTimestampService = new KeenTimestampService(configuredCatalog, true);

    final int notUnixTimestampCursor = 250_000;
    final AirbyteMessage message = buildMessageWithCursorValue(configuredCatalog, notUnixTimestampCursor);

    // 2020-10-14T01:09:49.200Z is hardcoded emitted at
    final JsonNode expectedJson = buildExpectedJsonWithTimestamp(notUnixTimestampCursor, "2020-10-14T01:09:49.200Z");

    final JsonNode jsonNode = keenTimestampService.injectTimestamp(message.getRecord());

    Assertions.assertEquals(jsonNode, expectedJson);
  }

  @Test
  void shouldInjectEmittedAtWhenCursorIsUnparsableAndRemoveFieldFromMap() throws IOException {
    final ConfiguredAirbyteCatalog configuredCatalog = readConfiguredCatalogFromFile("string_cursor_catalog.json");

    final KeenTimestampService keenTimestampService = new KeenTimestampService(configuredCatalog, true);

    final Map<String, List<String>> cursorFieldMap = keenTimestampService.getStreamCursorFields();
    Assertions.assertEquals(cursorFieldMap.size(), 1);

    final AirbyteMessage message = buildMessageWithCursorValue(configuredCatalog, "some_text");

    // 2020-10-14T01:09:49.200Z is hardcoded emitted at
    final JsonNode expectedJson = buildExpectedJsonWithTimestamp("\"some_text\"", "2020-10-14T01:09:49.200Z");

    final JsonNode jsonNode = keenTimestampService.injectTimestamp(message.getRecord());

    Assertions.assertEquals(jsonNode, expectedJson);
    Assertions.assertEquals(cursorFieldMap.size(), 0);
  }

  @Test
  void shouldInjectEmittedAtWhenCursorIsValidAndInferenceIsDisabled() throws IOException {
    final ConfiguredAirbyteCatalog configuredCatalog = readConfiguredCatalogFromFile("number_cursor_catalog.json");
    final KeenTimestampService keenTimestampService = new KeenTimestampService(configuredCatalog, false);

    final int secondsCursor = 1628080068;
    final AirbyteMessage message = buildMessageWithCursorValue(configuredCatalog, secondsCursor);

    // 2020-10-14T01:09:49.200Z is hardcoded emitted at
    final JsonNode expectedJson = buildExpectedJsonWithTimestamp(secondsCursor, "2020-10-14T01:09:49.200Z");
    final JsonNode jsonNode = keenTimestampService.injectTimestamp(message.getRecord());

    Assertions.assertEquals(jsonNode, expectedJson);
  }

  @Test
  void shouldInjectTimestampWhenCursorIsNestedField() throws IOException {
    final ConfiguredAirbyteCatalog configuredCatalog = readConfiguredCatalogFromFile("nested_cursor_catalog.json");
    final KeenTimestampService keenTimestampService = new KeenTimestampService(configuredCatalog, true);

    final int secondsCursor = 1628080068;
    final AirbyteMessage message = buildMessageWithCursorValue(configuredCatalog,
        ImmutableMap.builder().put("nestedProperty", secondsCursor).build());

    final String nestedJson = String.format("{\"nestedProperty\": %s}", secondsCursor);

    final JsonNode expectedJson = buildExpectedJsonWithTimestamp(nestedJson, "2021-08-04T12:27:48Z");
    final JsonNode jsonNode = keenTimestampService.injectTimestamp(message.getRecord());

    Assertions.assertEquals(jsonNode, expectedJson);
  }

  private <T> AirbyteMessage buildMessageWithCursorValue(final ConfiguredAirbyteCatalog configuredCatalog, final T cursorValue) {
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

  private <T> JsonNode buildExpectedJsonWithTimestamp(final T value, final String parsedTimestamp)
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

  private ConfiguredAirbyteCatalog readConfiguredCatalogFromFile(final String fileName)
      throws IOException {
    final AirbyteCatalog catalog = Jsons.deserialize(MoreResources.readResource(fileName), AirbyteCatalog.class);
    return new ConfiguredAirbyteCatalog()
        .withStreams(catalog.getStreams()
            .stream()
            .map(this::toConfiguredStreamWithCursors)
            .collect(Collectors.toList()));
  }

  public ConfiguredAirbyteStream toConfiguredStreamWithCursors(final AirbyteStream stream) {
    return new ConfiguredAirbyteStream()
        .withStream(stream)
        .withCursorField(stream.getDefaultCursorField());
  }

}
