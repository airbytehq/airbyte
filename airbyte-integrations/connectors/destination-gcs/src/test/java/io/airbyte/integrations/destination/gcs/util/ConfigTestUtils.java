/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs.util;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.gcs.GcsDestinationConfig;

public class ConfigTestUtils {

  public static JsonNode getBaseConfig(final JsonNode formatConfig) {
    return Jsons.deserialize("{\n"
        + "  \"gcs_bucket_name\": \"test-bucket-name\",\n"
        + "  \"gcs_bucket_path\": \"test_path\",\n"
        + "  \"gcs_bucket_region\": \"us-east-2\","
        + "  \"credential\": {\n"
        + "    \"credential_type\": \"HMAC_KEY\",\n"
        + "    \"hmac_key_access_id\": \"some_hmac_key\",\n"
        + "    \"hmac_key_secret\": \"some_key_secret\"\n"
        + "  },"
        + "  \"format\": " + formatConfig
        + "}");

  }

  public static void assertBaseConfig(final GcsDestinationConfig gcsDestinationConfig) {
    assertEquals("test-bucket-name", gcsDestinationConfig.getBucketName());
    assertEquals("test_path", gcsDestinationConfig.getBucketPath());
    assertEquals("us-east-2", gcsDestinationConfig.getBucketRegion());
  }

}
