/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.csv;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.record_buffer.BufferStorage;
import io.airbyte.integrations.destination.record_buffer.FileBuffer;
import io.airbyte.integrations.destination.record_buffer.InMemoryBuffer;
import io.airbyte.integrations.destination.s3.S3Format;
import io.airbyte.integrations.destination.s3.csv.S3CsvFormatConfig.Flattening;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
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
  private static final String CSV_FILE_EXTENSION = ".csv";
  private static final CSVFormat csvFormat = CSVFormat.newFormat(',');

  @Test
  public void testUncompressedDefaultCsvFormatWriter() throws Exception {
    runTest(new InMemoryBuffer(CSV_FILE_EXTENSION), CSVFormat.DEFAULT, false, 350L, 365L, null,
        getExpectedString(CSVFormat.DEFAULT));
  }

  @Test
  public void testUncompressedCsvWriter() throws Exception {
    runTest(new InMemoryBuffer(CSV_FILE_EXTENSION), csvFormat, false, 320L, 335L, null,
        getExpectedString(csvFormat));
  }

  @Test
  public void testCompressedCsvWriter() throws Exception {
    runTest(new InMemoryBuffer(CSV_FILE_EXTENSION), csvFormat, true, 170L, 190L, null,
        getExpectedString(csvFormat));
  }

  @Test
  public void testCompressedCsvFileWriter() throws Exception {
    runTest(new FileBuffer(CSV_FILE_EXTENSION), csvFormat, true, 170L, 190L, null,
        getExpectedString(csvFormat));
  }

  private static String getExpectedString(final CSVFormat csvFormat) {
    String expectedData = Jsons.serialize(MESSAGE_DATA);
    if (csvFormat.equals(CSVFormat.DEFAULT)) {
      expectedData = "\"" + expectedData.replace("\"", "\"\"") + "\"";
    }
    return expectedData;
  }

  @Test
  public void testFlattenCompressedCsvFileWriter() throws Exception {
    final String expectedData = "true,string value,10000,{\"array_column\":[1,2,3]}";
    runTest(new FileBuffer(CSV_FILE_EXTENSION), CSVFormat.newFormat(',').withRecordSeparator('\n'), true, 135L, 150L,
        new S3CsvFormatConfig(Jsons.jsonNode(Map.of(
            "format_type", S3Format.CSV,
            "flattening", Flattening.ROOT_LEVEL.getValue()))),
        expectedData + expectedData);
  }

  private static void runTest(final BufferStorage buffer,
                              final CSVFormat csvFormat,
                              final boolean withCompression,
                              final Long minExpectedByte,
                              final Long maxExpectedByte,
                              final S3CsvFormatConfig config,
                              final String expectedData)
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
        final BufferedReader reader = new BufferedReader(new InputStreamReader(inputStream, StandardCharsets.UTF_8));
        final StringBuilder tmpData = new StringBuilder();
        String line;
        while (reader.ready()) {
          line = reader.readLine();
          tmpData.append(line
              // remove uuid
              .substring(UUID.randomUUID().toString().length() + 1)
              // remove timestamp
              .replaceAll("\\A[0-9]+,", ""));
        }
        actualData = tmpData.toString();
      }
      assertEquals(expectedData, actualData);
    }
    assertFalse(outputFile.exists());
  }

}
