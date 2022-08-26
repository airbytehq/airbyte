/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.parquet;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.amazonaws.util.IOUtils;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.destination.record_buffer.SerializableBuffer;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.nio.file.Files;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.apache.avro.generic.GenericData;
import org.apache.avro.generic.GenericData.Record;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.parquet.avro.AvroReadSupport;
import org.apache.parquet.hadoop.ParquetReader;
import org.junit.jupiter.api.Test;

public class ParquetSerializedBufferTest {

  private static final JsonNode MESSAGE_DATA = Jsons.jsonNode(Map.of(
      "field1", 10000,
      "column2", "string value",
      "another field", true,
      "nested_column", Map.of("array_column", List.of(1, 2, 3)),
      "datetime_with_timezone", "2022-05-12T15:35:44.192950Z"));
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
      Field.of("nested_column", JsonSchemaType.OBJECT),
      Field.of("datetime_with_timezone", JsonSchemaType.STRING_TIMESTAMP_WITH_TIMEZONE));
  private static final ConfiguredAirbyteCatalog catalog = CatalogHelpers.createConfiguredAirbyteCatalog(STREAM, null, FIELDS);

  @Test
  public void testUncompressedParquetWriter() throws Exception {
    final S3DestinationConfig config = S3DestinationConfig.getS3DestinationConfig(Jsons.jsonNode(Map.of(
        "format", Map.of(
            "format_type", "parquet"),
        "s3_bucket_name", "test",
        "s3_bucket_region", "us-east-2")));
    runTest(195L, 215L, config, getExpectedString());
  }

  @Test
  public void testCompressedParquetWriter() throws Exception {
    final S3DestinationConfig config = S3DestinationConfig.getS3DestinationConfig(Jsons.jsonNode(Map.of(
        "format", Map.of(
            "format_type", "parquet",
            "compression_codec", "GZIP"),
        "s3_bucket_name", "test",
        "s3_bucket_region", "us-east-2")));
    // TODO: Compressed parquet is the same size as uncompressed??
    runTest(195L, 215L, config, getExpectedString());
  }

  private static String getExpectedString() {
    return "{\"_airbyte_ab_id\": \"<UUID>\", \"_airbyte_emitted_at\": \"<timestamp>\", "
        + "\"field1\": 10000.0, \"another_field\": true, "
        + "\"nested_column\": {\"_airbyte_additional_properties\": {\"array_column\": \"[1,2,3]\"}}, "
        + "\"column2\": \"string value\", "
        + "\"datetime_with_timezone\": 1652369744192000, "
        + "\"_airbyte_additional_properties\": null}";
  }

  private static void runTest(final Long minExpectedByte,
                              final Long maxExpectedByte,
                              final S3DestinationConfig config,
                              final String expectedData)
      throws Exception {
    final File tempFile = Files.createTempFile(UUID.randomUUID().toString(), ".parquet").toFile();
    try (final SerializableBuffer writer = ParquetSerializedBuffer.createFunction(config).apply(streamPair, catalog)) {
      writer.accept(message);
      writer.accept(message);
      writer.flush();
      // some data are randomized (uuid, timestamp, compression?) so the expected byte count is not always
      // deterministic
      assertTrue(minExpectedByte <= writer.getByteCount() && writer.getByteCount() <= maxExpectedByte,
          String.format("Expected size between %d and %d, but actual size was %d",
              minExpectedByte, maxExpectedByte, writer.getByteCount()));
      final InputStream in = writer.getInputStream();
      try (final FileOutputStream outFile = new FileOutputStream(tempFile)) {
        IOUtils.copy(in, outFile);
      }
      try (final ParquetReader<Record> parquetReader =
          ParquetReader.<GenericData.Record>builder(new AvroReadSupport<>(), new Path(tempFile.getAbsolutePath()))
              .withConf(new Configuration())
              .build()) {
        GenericData.Record record;
        while ((record = parquetReader.read()) != null) {
          record.put("_airbyte_ab_id", "<UUID>");
          record.put("_airbyte_emitted_at", "<timestamp>");
          final String actualData = record.toString();
          assertEquals(expectedData, actualData);
        }
      }
    } finally {
      Files.deleteIfExists(tempFile.toPath());
    }
  }

}
