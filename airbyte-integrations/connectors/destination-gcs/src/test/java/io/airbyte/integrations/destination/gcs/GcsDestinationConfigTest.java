/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.destination.gcs.credential.GcsCredentialConfig;
import io.airbyte.integrations.destination.gcs.credential.GcsHmacKeyCredentialConfig;
import io.airbyte.integrations.destination.s3.S3FormatConfig;
import io.airbyte.integrations.destination.s3.avro.S3AvroFormatConfig;
import java.io.IOException;
import org.junit.jupiter.api.Test;

class GcsDestinationConfigTest {

  @Test
  public void testGetGcsDestinationConfig() throws IOException {
    JsonNode configJson = Jsons.deserialize(MoreResources.readResource("test_config.json"));

    GcsDestinationConfig config = GcsDestinationConfig.getGcsDestinationConfig(configJson);
    assertEquals("test_bucket", config.getBucketName());
    assertEquals("test_path", config.getBucketPath());
    assertEquals("us-west1", config.getBucketRegion());

    GcsCredentialConfig credentialConfig = config.getCredentialConfig();
    assertTrue(credentialConfig instanceof GcsHmacKeyCredentialConfig);

    GcsHmacKeyCredentialConfig hmacKeyConfig = (GcsHmacKeyCredentialConfig) credentialConfig;
    assertEquals("test_access_id", hmacKeyConfig.getHmacKeyAccessId());
    assertEquals("test_secret", hmacKeyConfig.getHmacKeySecret());

    S3FormatConfig formatConfig = config.getFormatConfig();
    assertTrue(formatConfig instanceof S3AvroFormatConfig);

    S3AvroFormatConfig avroFormatConfig = (S3AvroFormatConfig) formatConfig;
    assertEquals("deflate-5", avroFormatConfig.getCodecFactory().toString());
  }

}
