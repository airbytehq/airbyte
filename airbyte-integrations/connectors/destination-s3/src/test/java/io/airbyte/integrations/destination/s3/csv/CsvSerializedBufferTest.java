/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.csv;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.destination.record_buffer.BufferStorage;
import io.airbyte.integrations.destination.record_buffer.FileBuffer;
import io.airbyte.integrations.destination.record_buffer.InMemoryBuffer;
import io.airbyte.integrations.destination.s3.S3Format;
import io.airbyte.integrations.destination.s3.csv.S3CsvFormatConfig.Flattening;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import java.io.BufferedReader;
import java.io.File;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.zip.GZIPInputStream;
import org.apache.commons.csv.CSVFormat;
import org.junit.jupiter.api.Test;

public class CsvSerializedBufferTest {

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
  protected static final List<Field> FIELDS = List.of(
      Field.of("field1", JsonSchemaType.NUMBER),
      Field.of("column2", JsonSchemaType.STRING),
      Field.of("another field", JsonSchemaType.BOOLEAN),
      Field.of("nested_column", JsonSchemaType.OBJECT));
  private static final ConfiguredAirbyteCatalog catalog = CatalogHelpers.createConfiguredAirbyteCatalog(STREAM, null, FIELDS);
  private static final String CSV_FILE_EXTENSION = ".csv";

  @Test
  public void testUncompressedDefaultCsvFormatWriter() throws Exception {
    runTest(new InMemoryBuffer(CSV_FILE_EXTENSION), CSVFormat.DEFAULT, false, 395L, 405L, null);
  }

  @Test
  public void testUncompressedCsvWriter() throws Exception {
    runTest(new InMemoryBuffer(CSV_FILE_EXTENSION), CSVFormat.newFormat(','), false, 355L, 365L, null);
  }

  @Test
  public void testCompressedCsvWriter() throws Exception {
    runTest(new InMemoryBuffer(CSV_FILE_EXTENSION), CSVFormat.newFormat(','), true, 175L, 190L, null);
  }

  @Test
  public void testCompressedCsvFileWriter() throws Exception {
    runTest(new FileBuffer(CSV_FILE_EXTENSION), CSVFormat.newFormat(','), true, 175L, 190L, null);
  }

  @Test
  public void testFlattenCompressedCsvFileWriter() throws Exception {
    runTest(new FileBuffer(CSV_FILE_EXTENSION), CSVFormat.newFormat(',').withRecordSeparator('\n'), true, 140L, 160L,
        new S3CsvFormatConfig(Jsons.jsonNode(Map.of(
            "format_type", S3Format.CSV,
            "flattening", Flattening.ROOT_LEVEL.getValue()))));
  }

  private static void runTest(final BufferStorage buffer,
                              final CSVFormat csvFormat,
                              final boolean withCompression,
                              final Long minExpectedByte,
                              final Long maxExpectedByte,
                              final S3CsvFormatConfig config)
      throws Exception {
    final File outputFile = buffer.getFile();
    try (final CsvSerializedBuffer writer = (CsvSerializedBuffer) CsvSerializedBuffer
        .createFunction(config, () -> buffer)
        .apply(streamPair, catalog)) {
      writer.withCsvFormat(csvFormat);
      writer.withCompression(withCompression);
      writer.accept(message);
      writer.accept(message);
      writer.flush();
      // some data are randomized (uuid, timestamp, compression?) so the expected byte count is not always
      // deterministic
      assertTrue(minExpectedByte <= writer.getByteCount() && writer.getByteCount() <= maxExpectedByte,
          String.format("Expected size between %d and %d, but actual size was %d",
              minExpectedByte, maxExpectedByte, writer.getByteCount()));
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
      final String actualData;
      if (config == null) {
        actualData = new String(inputStream.readAllBytes(), StandardCharsets.UTF_8)
            // remove the UUID string at the beginning
            .substring(UUID.randomUUID().toString().length() + 1)
            // remove the last part of the string with random timestamp
            .substring(0, expectedData.length());
      } else {
        final BufferedReader reader = new BufferedReader(new InputStreamReader(inputStream));
        final StringBuilder tmpData = new StringBuilder();
        String line;
        do {
          line = reader.readLine();
          tmpData.append(line.substring(UUID.randomUUID().toString().length() + 1));
        } while ();
      }
      assertEquals(expectedData, actualData);
    }
    assertFalse(outputFile.exists());
  }

}
