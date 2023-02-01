/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.jsonl;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.record_buffer.BufferStorage;
import io.airbyte.integrations.destination.record_buffer.FileBuffer;
import io.airbyte.integrations.destination.record_buffer.InMemoryBuffer;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.io.File;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Map;
import java.util.zip.GZIPInputStream;
import org.junit.jupiter.api.Test;

public class JsonLSerializedBufferTest {

  private static final JsonNode MESSAGE_DATA = Jsons.jsonNode(Map.of(
      "field1", 10000,
      "column2", "string value",
      "another field", true,
      "nested_column", Map.of("array_column", List.of(1, 2, 3))));
  private static final String STREAM = "stream1";
  private static final AirbyteStreamNameNamespacePair streamPair = new AirbyteStreamNameNamespacePair(STREAM, null);
  private static final AirbyteRecordMessage message = new AirbyteRecordMessage()
      .withStream(STREAM)
      .withData(MESSAGE_DATA)
      .withEmittedAt(System.currentTimeMillis());
  protected static final List<Field> FIELDS = List.of(
      Field.of("field1", JsonSchemaType.NUMBER),
      Field.of("column2", JsonSchemaType.STRING),
      Field.of("another field", JsonSchemaType.BOOLEAN),
      Field.of("nested_column", JsonSchemaType.OBJECT));
  private static final ConfiguredAirbyteCatalog catalog = CatalogHelpers.createConfiguredAirbyteCatalog(STREAM, null, FIELDS);
  private static final String JSON_FILE_EXTENSION = ".jsonl";

  @Test
  public void testUncompressedJsonLFormatWriter() throws Exception {
    runTest(new InMemoryBuffer(JSON_FILE_EXTENSION), false, 425L, 435L, getExpectedString());
  }

  @Test
  public void testCompressedJsonLWriter() throws Exception {
    runTest(new FileBuffer(JSON_FILE_EXTENSION), true, 205L, 215L, getExpectedString());
  }

  private static String getExpectedString() {
    return Jsons.serialize(MESSAGE_DATA);
  }

  private static void runTest(final BufferStorage buffer,
                              final boolean withCompression,
                              final Long minExpectedByte,
                              final Long maxExpectedByte,
                              final String expectedData)
      throws Exception {
    final File outputFile = buffer.getFile();
    try (final JsonLSerializedBuffer writer = (JsonLSerializedBuffer) JsonLSerializedBuffer
        .createFunction(null, () -> buffer)
        .apply(streamPair, catalog)) {
      writer.withCompression(withCompression);
      writer.accept(message);
      writer.accept(message);
      writer.flush();
      // some data are randomized (uuid, timestamp, compression?) so the expected byte count is not always
      // deterministic
      assertTrue(minExpectedByte <= writer.getByteCount() && writer.getByteCount() <= maxExpectedByte,
          String.format("Expected size between %d and %d, but actual size was %d",
              minExpectedByte, maxExpectedByte, writer.getByteCount()));
      final InputStream inputStream;
      if (withCompression) {
        inputStream = new GZIPInputStream(writer.getInputStream());
      } else {
        inputStream = writer.getInputStream();
      }
      final JsonNode actualData = Jsons.deserialize(new String(inputStream.readAllBytes(), StandardCharsets.UTF_8));
      assertEquals(expectedData, Jsons.serialize(actualData.get("_airbyte_data")));
    }
    assertFalse(outputFile.exists());
  }

}
