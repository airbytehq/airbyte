/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.jsonl;

import static com.amazonaws.services.s3.internal.Constants.MB;
import static io.airbyte.integrations.destination.s3.util.StreamTransferManagerFactory.DEFAULT_PART_SIZE_MB;
import static org.junit.jupiter.api.Assertions.assertEquals;

import alex.mojaki.s3upload.StreamTransferManager;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.S3FormatConfig;
import io.airbyte.integrations.destination.s3.util.ConfigTestUtils;
import io.airbyte.integrations.destination.s3.util.StreamTransferManagerFactory;
import org.apache.commons.lang3.reflect.FieldUtils;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

@DisplayName("S3JsonlFormatConfig")
public class S3JsonlFormatConfigTest {

  @Test
  public void testHandlePartSizeConfig() throws IllegalAccessException {

    final JsonNode config = ConfigTestUtils.getBaseConfig(Jsons.deserialize("{\n"
        + "  \"format_type\": \"JSONL\"\n"
        + "}"));

    final S3DestinationConfig s3DestinationConfig = S3DestinationConfig
        .getS3DestinationConfig(config);
    ConfigTestUtils.assertBaseConfig(s3DestinationConfig);

    final S3FormatConfig formatConfig = s3DestinationConfig.getFormatConfig();
    assertEquals("JSONL", formatConfig.getFormat().name());

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
        + "  \"format_type\": \"JSONL\"\n"
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

}
