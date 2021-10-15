/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.csv;

import static com.amazonaws.services.s3.internal.Constants.MB;
import static org.junit.jupiter.api.Assertions.*;

import alex.mojaki.s3upload.StreamTransferManager;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.S3FormatConfig;
import io.airbyte.integrations.destination.s3.csv.S3CsvFormatConfig.Flattening;
import io.airbyte.integrations.destination.s3.util.ConfigTestUtils;
import io.airbyte.integrations.destination.s3.util.S3StreamTransferManagerHelper;
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
    } catch (Exception e) {
      assertTrue(e instanceof IllegalArgumentException);
    }
  }

  @Test
  public void testHandlePartSizeConfig() throws IllegalAccessException {

    JsonNode config = ConfigTestUtils.getBaseConfig(Jsons.deserialize("{\n"
        + "  \"format_type\": \"CSV\",\n"
        + "  \"flattening\": \"Root level flattening\",\n"
        + "  \"part_size_mb\": 6\n"
        + "}"));

    S3DestinationConfig s3DestinationConfig = S3DestinationConfig
        .getS3DestinationConfig(config);
    ConfigTestUtils.assertBaseConfig(s3DestinationConfig);

    S3FormatConfig formatConfig = s3DestinationConfig.getFormatConfig();
    assertEquals("CSV", formatConfig.getFormat().name());
    assertEquals(6, formatConfig.getPartSize());
    // Assert that is set properly in config
    StreamTransferManager streamTransferManager = S3StreamTransferManagerHelper.getDefault(
        s3DestinationConfig.getBucketName(), "objectKey", null,
        s3DestinationConfig.getFormatConfig().getPartSize());

    Integer partSizeBytes = (Integer) FieldUtils.readField(streamTransferManager, "partSize", true);
    assertEquals(MB * 6, partSizeBytes);
  }

  @Test
  public void testHandleAbsenceOfPartSizeConfig() throws IllegalAccessException {

    JsonNode config = ConfigTestUtils.getBaseConfig(Jsons.deserialize("{\n"
        + "  \"format_type\": \"CSV\",\n"
        + "  \"flattening\": \"Root level flattening\"\n"
        + "}"));

    S3DestinationConfig s3DestinationConfig = S3DestinationConfig
        .getS3DestinationConfig(config);
    ConfigTestUtils.assertBaseConfig(s3DestinationConfig);

    StreamTransferManager streamTransferManager = S3StreamTransferManagerHelper.getDefault(
        s3DestinationConfig.getBucketName(), "objectKey", null,
        s3DestinationConfig.getFormatConfig().getPartSize());

    Integer partSizeBytes = (Integer) FieldUtils.readField(streamTransferManager, "partSize", true);
    assertEquals(MB * 5, partSizeBytes); // 5MB is a default value if nothing provided explicitly
  }

}
