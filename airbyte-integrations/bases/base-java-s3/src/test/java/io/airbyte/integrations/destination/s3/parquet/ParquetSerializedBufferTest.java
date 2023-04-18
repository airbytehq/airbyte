/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.parquet;

import static io.airbyte.integrations.destination.s3.util.JavaProcessRunner.runProcess;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.amazonaws.util.IOUtils;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.record_buffer.SerializableBuffer;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaPrimitiveUtil.JsonSchemaPrimitive;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.nio.file.Files;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Stream;
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
      "string_array_column", Stream.of("test_string", null).toList(),
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
      Field.of("string_array_column", JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
          .withItems(JsonSchemaType.STRING).build()),
      Field.of("datetime_with_timezone", JsonSchemaType.STRING_TIMESTAMP_WITH_TIMEZONE));
  private static final ConfiguredAirbyteCatalog catalog = CatalogHelpers.createConfiguredAirbyteCatalog(STREAM, null, FIELDS);

  @Test
  public void testUncompressedParquetWriter() throws Exception {
    final S3DestinationConfig config = S3DestinationConfig.getS3DestinationConfig(Jsons.jsonNode(Map.of(
        "format", Map.of(
            "format_type", "parquet"),
        "s3_bucket_name", "test",
        "s3_bucket_region", "us-east-2")));
    runTest(225L, 245L, config, getExpectedString());
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
    runTest(225L, 245L, config, getExpectedString());
  }

  private static String resolveArchitecture() {
    return System.getProperty("os.name").replace(' ', '_') + "-" + System.getProperty("os.arch") + "-" + System.getProperty("sun.arch.data.model");
  }

  @Test
  public void testLzoCompressedParquet() throws Exception {
    final String currentDir = System.getProperty("user.dir");
    Runtime runtime = Runtime.getRuntime();
    final String architecture = resolveArchitecture();
    if (architecture.equals("Linux-amd64-64") || architecture.equals("Linux-x86_64-64")) {
      runProcess(currentDir, runtime, "/bin/sh", "-c", "apt-get update");
      runProcess(currentDir, runtime, "/bin/sh", "-c", "apt-get install lzop liblzo2-2 liblzo2-dev -y");
      runLzoParquetTest();
    } else if (architecture.equals("Linux-aarch64-64") || architecture.equals("Linux-arm64-64")) {
      runProcess(currentDir, runtime, "/bin/sh", "-c", "apt-get update");
      runProcess(currentDir, runtime, "/bin/sh", "-c", "apt-get install lzop liblzo2-2 liblzo2-dev " +
          "wget curl unzip zip build-essential maven git -y");
      runProcess(currentDir, runtime, "/bin/sh", "-c", "wget https://www.oberhumer.com/opensource/lzo/download/lzo-2.10.tar.gz -P /usr/local/tmp");
      runProcess("/usr/local/tmp/", runtime, "/bin/sh", "-c", "tar xvfz lzo-2.10.tar.gz");
      runProcess("/usr/local/tmp/lzo-2.10/", runtime, "/bin/sh", "-c", "./configure --enable-shared --prefix /usr/local/lzo-2.10");
      runProcess("/usr/local/tmp/lzo-2.10/", runtime, "/bin/sh", "-c", "make && make install");
      runProcess(currentDir, runtime, "/bin/sh", "-c", "git clone https://github.com/twitter/hadoop-lzo.git /usr/lib/hadoop/lib/hadoop-lzo/");
      runProcess(currentDir, runtime, "/bin/sh", "-c", "curl -s https://get.sdkman.io | bash");
      runProcess(currentDir, runtime, "/bin/bash", "-c", "source /root/.sdkman/bin/sdkman-init.sh;" +
          " sdk install java 8.0.342-librca;" +
          " sdk use java 8.0.342-librca;" +
          " cd /usr/lib/hadoop/lib/hadoop-lzo/ " +
          "&& C_INCLUDE_PATH=/usr/local/lzo-2.10/include " +
          "LIBRARY_PATH=/usr/local/lzo-2.10/lib mvn clean package");
      runProcess(currentDir, runtime, "/bin/sh", "-c",
          "find /usr/lib/hadoop/lib/hadoop-lzo/ -name '*libgplcompression*' -exec cp {} /usr/lib/ \\;");
      runLzoParquetTest();
    }
  }

  private void runLzoParquetTest() throws Exception {
    final S3DestinationConfig config = S3DestinationConfig.getS3DestinationConfig(Jsons.jsonNode(Map.of(
        "format", Map.of(
            "format_type", "parquet",
            "compression_codec", "LZO"),
        "s3_bucket_name", "test",
        "s3_bucket_region", "us-east-2")));
    runTest(225L, 245L, config, getExpectedString());
  }

  private static String getExpectedString() {
    return "{\"_airbyte_ab_id\": \"<UUID>\", \"_airbyte_emitted_at\": \"<timestamp>\", "
        + "\"field1\": 10000.0, \"another_field\": true, "
        + "\"nested_column\": {\"_airbyte_additional_properties\": {\"array_column\": \"[1,2,3]\"}}, "
        + "\"column2\": \"string value\", "
        + "\"string_array_column\": [\"test_string\", null], "
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
          ParquetReader.<Record>builder(new AvroReadSupport<>(), new Path(tempFile.getAbsolutePath()))
              .withConf(new Configuration())
              .build()) {
        Record record;
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
