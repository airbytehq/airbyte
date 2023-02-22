/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.avro;

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
import java.util.List;
import java.util.Map;
import org.apache.avro.file.DataFileReader;
import org.apache.avro.file.SeekableByteArrayInput;
import org.apache.avro.generic.GenericData.Record;
import org.apache.avro.generic.GenericDatumReader;
import org.junit.jupiter.api.Test;

public class AvroSerializedBufferTest {

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

  @Test
  public void testSnappyAvroWriter() throws Exception {
    final S3AvroFormatConfig config = new S3AvroFormatConfig(Jsons.jsonNode(Map.of("compression_codec", Map.of(
        "codec", "snappy"))));
    runTest(new InMemoryBuffer(AvroSerializedBuffer.DEFAULT_SUFFIX), 964L, 985L, config, getExpectedString());
  }

  @Test
  public void testGzipAvroFileWriter() throws Exception {
    final S3AvroFormatConfig config = new S3AvroFormatConfig(Jsons.jsonNode(Map.of("compression_codec", Map.of(
        "codec", "zstandard",
        "compression_level", 20,
        "include_checksum", true))));
    runTest(new FileBuffer(AvroSerializedBuffer.DEFAULT_SUFFIX), 970L, 985L, config, getExpectedString());
  }

  @Test
  public void testUncompressedAvroWriter() throws Exception {
    final S3AvroFormatConfig config = new S3AvroFormatConfig(Jsons.jsonNode(Map.of("compression_codec", Map.of(
        "codec", "no compression"))));
    runTest(new InMemoryBuffer(AvroSerializedBuffer.DEFAULT_SUFFIX), 1010L, 1020L, config, getExpectedString());
  }

  private static String getExpectedString() {
    return "{\"_airbyte_ab_id\": \"<UUID>\", \"_airbyte_emitted_at\": \"<timestamp>\", "
        + "\"field1\": 10000.0, \"another_field\": true, "
        + "\"nested_column\": {\"_airbyte_additional_properties\": {\"array_column\": \"[1,2,3]\"}}, "
        + "\"column2\": \"string value\", "
        + "\"_airbyte_additional_properties\": null}";
  }

  private static void runTest(final BufferStorage buffer,
                              final Long minExpectedByte,
                              final Long maxExpectedByte,
                              final S3AvroFormatConfig config,
                              final String expectedData)
      throws Exception {
    final File outputFile = buffer.getFile();
    try (final AvroSerializedBuffer writer = (AvroSerializedBuffer) AvroSerializedBuffer
        .createFunction(config, () -> buffer)
        .apply(streamPair, catalog)) {
      writer.accept(message);
      writer.accept(message);
      writer.flush();
      // some data are randomized (uuid, timestamp, compression?) so the expected byte count is not always
      // deterministic
      assertTrue(minExpectedByte <= writer.getByteCount() && writer.getByteCount() <= maxExpectedByte,
          String.format("Expected size between %d and %d, but actual size was %d",
              minExpectedByte, maxExpectedByte, writer.getByteCount()));
      final InputStream in = writer.getInputStream();
      try (final DataFileReader<Record> dataFileReader =
          new DataFileReader<>(new SeekableByteArrayInput(in.readAllBytes()), new GenericDatumReader<>())) {
        while (dataFileReader.hasNext()) {
          final Record record = dataFileReader.next();
          record.put("_airbyte_ab_id", "<UUID>");
          record.put("_airbyte_emitted_at", "<timestamp>");
          final String actualData = record.toString();
          assertEquals(expectedData, actualData);
        }
      }
    }
    assertFalse(outputFile.exists());
  }

}
