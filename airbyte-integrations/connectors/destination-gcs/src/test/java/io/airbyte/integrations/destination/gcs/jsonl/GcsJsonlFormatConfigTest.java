/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs.jsonl;

import static com.amazonaws.services.s3.internal.Constants.MB;
import static io.airbyte.integrations.destination.s3.util.StreamTransferManagerFactory.DEFAULT_PART_SIZE_MB;
import static org.junit.jupiter.api.Assertions.assertEquals;

import alex.mojaki.s3upload.StreamTransferManager;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.gcs.GcsDestinationConfig;
import io.airbyte.integrations.destination.gcs.util.ConfigTestUtils;
import io.airbyte.integrations.destination.s3.S3FormatConfig;
import io.airbyte.integrations.destination.s3.util.StreamTransferManagerFactory;
import org.apache.commons.lang3.reflect.FieldUtils;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

@DisplayName("GcsJsonlFormatConfig")
public class GcsJsonlFormatConfigTest {

  @Test
  public void testHandlePartSizeConfig() throws IllegalAccessException {

    final JsonNode config = ConfigTestUtils.getBaseConfig(Jsons.deserialize("{\n"
        + "  \"format_type\": \"JSONL\"\n"
        + "}"));

    final GcsDestinationConfig gcsDestinationConfig = GcsDestinationConfig
        .getGcsDestinationConfig(config);
    ConfigTestUtils.assertBaseConfig(gcsDestinationConfig);

    final S3FormatConfig formatConfig = gcsDestinationConfig.getFormatConfig();
    assertEquals("JSONL", formatConfig.getFormat().name());

    // Assert that is set properly in config
    final StreamTransferManager streamTransferManager = StreamTransferManagerFactory
        .create(gcsDestinationConfig.getBucketName(), "objectKey", null)
        .get();

    final Integer partSizeBytes = (Integer) FieldUtils.readField(streamTransferManager, "partSize", true);
    assertEquals(MB * DEFAULT_PART_SIZE_MB, partSizeBytes);
  }

  @Test
  public void testHandleAbsenceOfPartSizeConfig() throws IllegalAccessException {

    final JsonNode config = ConfigTestUtils.getBaseConfig(Jsons.deserialize("{\n"
        + "  \"format_type\": \"JSONL\"\n"
        + "}"));

    final GcsDestinationConfig gcsDestinationConfig = GcsDestinationConfig
        .getGcsDestinationConfig(config);
    ConfigTestUtils.assertBaseConfig(gcsDestinationConfig);

    final StreamTransferManager streamTransferManager = StreamTransferManagerFactory
        .create(gcsDestinationConfig.getBucketName(), "objectKey", null)
        .get();

    final Integer partSizeBytes = (Integer) FieldUtils.readField(streamTransferManager, "partSize", true);
    assertEquals(MB * DEFAULT_PART_SIZE_MB, partSizeBytes);
  }

}
