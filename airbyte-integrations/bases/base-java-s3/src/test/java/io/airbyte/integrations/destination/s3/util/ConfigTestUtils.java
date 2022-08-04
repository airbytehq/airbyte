/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.util;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.credential.S3AccessKeyCredentialConfig;

public class ConfigTestUtils {

  public static JsonNode getBaseConfig(final JsonNode formatConfig) {
    return Jsons.deserialize("{\n"
        + "  \"s3_endpoint\": \"some_test-endpoint\",\n"
        + "  \"s3_bucket_name\": \"test-bucket-name\",\n"
        + "  \"s3_bucket_path\": \"test_path\",\n"
        + "  \"s3_bucket_region\": \"us-east-2\",\n"
        + "  \"access_key_id\": \"some-test-key-id\",\n"
        + "  \"secret_access_key\": \"some-test-access-key\",\n"
        + "  \"format\": " + formatConfig
        + "}");
  }

  public static void assertBaseConfig(final S3DestinationConfig s3DestinationConfig) {
    assertEquals("some_test-endpoint", s3DestinationConfig.getEndpoint());
    assertEquals("test-bucket-name", s3DestinationConfig.getBucketName());
    assertEquals("test_path", s3DestinationConfig.getBucketPath());
    assertEquals("us-east-2", s3DestinationConfig.getBucketRegion());
    final S3AccessKeyCredentialConfig credentialConfig = (S3AccessKeyCredentialConfig) s3DestinationConfig.getS3CredentialConfig();
    assertEquals("some-test-key-id", credentialConfig.getAccessKeyId());
    assertEquals("some-test-access-key", credentialConfig.getSecretAccessKey());
  }

}
