/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.csv;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.destination.record_buffer.FileRecordBuffer;
import io.airbyte.integrations.destination.record_buffer.InMemoryRecordBuffer;
import io.airbyte.integrations.destination.record_buffer.RecordBufferStorage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.io.File;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.zip.GZIPInputStream;
import org.apache.commons.csv.CSVFormat;
import org.junit.jupiter.api.Test;

public class CsvRecordBufferTest {

  private static final JsonNode MESSAGE_DATA = Jsons.jsonNode(Map.of(
      "field1", 10000,
      "column2", "string value",
      "another field", true,
      "nested_column", Map.of(
          "column", "value",
          "array_column", List.of(1, 2, 3))));
  private static final String STREAM = "stream1";
  private static final AirbyteStreamNameNamespacePair streamPair = new AirbyteStreamNameNamespacePair(STREAM, null);
  private static final AirbyteRecordMessage message = new AirbyteRecordMessage()
      .withStream(STREAM)
      .withData(MESSAGE_DATA)
      .withEmittedAt(System.currentTimeMillis());
  private static final ConfiguredAirbyteCatalog catalog = mock(ConfiguredAirbyteCatalog.class);

  @Test
  public void testUncompressedDefaultCsvFormatWriter() throws Exception {
    runTest(new InMemoryRecordBuffer(), CSVFormat.DEFAULT, false, 395L, 405L);
  }

  @Test
  public void testUncompressedCsvWriter() throws Exception {
    runTest(new InMemoryRecordBuffer(), CSVFormat.newFormat(','), false, 355L, 365L);
  }

  @Test
  public void testCompressedCsvWriter() throws Exception {
    runTest(new InMemoryRecordBuffer(), CSVFormat.newFormat(','), true, 180L, 190L);
  }

  @Test
  public void testCompressedCsvFileWriter() throws Exception {
    runTest(new FileRecordBuffer(), CSVFormat.newFormat(','), true, 180L, 190L);
  }

  private static void runTest(final RecordBufferStorage buffer,
                              final CSVFormat csvFormat,
                              final boolean withCompression,
                              final Long minExpectedByte,
                              final Long maxExpectedByte)
      throws Exception {
    final File outputFile = buffer.getFile();
    try (final CsvRecordBuffer writer = (CsvRecordBuffer) CsvRecordBuffer
        .createFunction(null, () -> buffer)
        .apply(streamPair, catalog)) {
      writer.withCsvFormat(csvFormat);
      writer.withCompression(withCompression);
      writer.accept(message);
      writer.accept(message);
      writer.flush();
      // some data are randomized (uuid, timestamp, compression?) so the expected byte count is not always
      // deterministic
      assertTrue(minExpectedByte < writer.getByteCount() && writer.getByteCount() < maxExpectedByte,
          String.format("actual size was %d", writer.getByteCount()));
      String expectedData = Jsons.serialize(MESSAGE_DATA);
      if (csvFormat.equals(CSVFormat.DEFAULT)) {
        expectedData = "\"" + expectedData.replace("\"", "\"\"") + "\"";
      }
      final InputStream inputStream;
      if (withCompression) {
        inputStream = new GZIPInputStream(writer.getInputStream());
      } else {
        inputStream = writer.getInputStream();
      }
      final String actualData = new String(inputStream.readAllBytes(), StandardCharsets.UTF_8)
          // remove the UUID string at the beginning
          .substring(UUID.randomUUID().toString().length() + 1)
          // remove the last part of the string with random timestamp
          .substring(0, expectedData.length());
      assertEquals(expectedData, actualData);
    }
    assertFalse(outputFile.exists());
  }

}
