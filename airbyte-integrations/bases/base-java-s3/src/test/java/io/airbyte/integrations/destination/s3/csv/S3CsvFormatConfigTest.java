/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.csv;

import static com.amazonaws.services.s3.internal.Constants.MB;
import static io.airbyte.integrations.destination.s3.util.StreamTransferManagerFactory.DEFAULT_PART_SIZE_MB;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import alex.mojaki.s3upload.StreamTransferManager;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.S3DestinationConstants;
import io.airbyte.integrations.destination.s3.S3FormatConfig;
import io.airbyte.integrations.destination.s3.csv.S3CsvFormatConfig.Flattening;
import io.airbyte.integrations.destination.s3.util.CompressionType;
import io.airbyte.integrations.destination.s3.util.ConfigTestUtils;
import io.airbyte.integrations.destination.s3.util.StreamTransferManagerFactory;
import org.apache.commons.lang3.reflect.FieldUtils;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

@DisplayName("S3CsvFormatConfig")
public class S3CsvFormatConfigTest {

  @Test
  @DisplayName("Flattening enums can be created from value string")
  public void testFlatteningCreationFromString() {
    assertEquals(Flattening.NO, Flattening.fromValue("no flattening"));
    assertEquals(Flattening.ROOT_LEVEL, Flattening.fromValue("root level flattening"));
    try {
      Flattening.fromValue("invalid flattening value");
    } catch (final Exception e) {
      assertTrue(e instanceof IllegalArgumentException);
    }
  }

  @Test
  public void testHandlePartSizeConfig() throws IllegalAccessException {

    final JsonNode config = ConfigTestUtils.getBaseConfig(Jsons.deserialize("{\n"
        + "  \"format_type\": \"CSV\",\n"
        + "  \"flattening\": \"Root level flattening\"\n"
        + "}"));

    final S3DestinationConfig s3DestinationConfig = S3DestinationConfig
        .getS3DestinationConfig(config);
    ConfigTestUtils.assertBaseConfig(s3DestinationConfig);

    final S3FormatConfig formatConfig = s3DestinationConfig.getFormatConfig();
    assertEquals("CSV", formatConfig.getFormat().name());
    // Assert that is set properly in config
    final StreamTransferManager streamTransferManager = StreamTransferManagerFactory
        .create(s3DestinationConfig.getBucketName(), "objectKey", null)
        .get();

    final Integer partSizeBytes = (Integer) FieldUtils.readField(streamTransferManager, "partSize", true);
    assertEquals(MB * DEFAULT_PART_SIZE_MB, partSizeBytes);
  }

  @Test
  public void testHandleAbsenceOfPartSizeConfig() throws IllegalAccessException {

    final JsonNode config = ConfigTestUtils.getBaseConfig(Jsons.deserialize("{\n"
        + "  \"format_type\": \"CSV\",\n"
        + "  \"flattening\": \"Root level flattening\"\n"
        + "}"));

    final S3DestinationConfig s3DestinationConfig = S3DestinationConfig
        .getS3DestinationConfig(config);
    ConfigTestUtils.assertBaseConfig(s3DestinationConfig);

    final StreamTransferManager streamTransferManager = StreamTransferManagerFactory
        .create(s3DestinationConfig.getBucketName(), "objectKey", null)
        .get();

    final Integer partSizeBytes = (Integer) FieldUtils.readField(streamTransferManager, "partSize", true);
    assertEquals(MB * DEFAULT_PART_SIZE_MB, partSizeBytes);
  }

  @Test
  public void testGzipCompressionConfig() {
    // without gzip compression config
    final JsonNode configWithoutGzipCompression = ConfigTestUtils.getBaseConfig(Jsons.deserialize("{\n"
        + "  \"format_type\": \"CSV\"\n"
        + "}"));
    final S3DestinationConfig s3ConfigWithoutGzipCompression = S3DestinationConfig.getS3DestinationConfig(configWithoutGzipCompression);
    assertEquals(
        S3DestinationConstants.DEFAULT_COMPRESSION_TYPE,
        ((S3CsvFormatConfig) s3ConfigWithoutGzipCompression.getFormatConfig()).getCompressionType());

    // with gzip compression config
    final JsonNode configWithGzipCompression = ConfigTestUtils.getBaseConfig(Jsons.deserialize("{\n"
        + "  \"format_type\": \"CSV\",\n"
        + "  \"gzip_compression\": false\n"
        + "}"));
    final S3DestinationConfig gcsConfigWithGzipCompression = S3DestinationConfig.getS3DestinationConfig(configWithGzipCompression);
    assertEquals(
        CompressionType.GZIP,
        ((S3CsvFormatConfig) gcsConfigWithGzipCompression.getFormatConfig()).getCompressionType());
  }

}
