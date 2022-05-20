/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import static org.junit.jupiter.api.Assertions.*;

import io.airbyte.integrations.destination.s3.credential.S3AccessKeyCredentialConfig;
import org.junit.jupiter.api.Test;

class S3DestinationConfigTest {

  private static final S3DestinationConfig CONFIG = S3DestinationConfig.create("test-bucket", "test-path", "test-region")
      .withEndpoint("test-endpoint")
      .withPartSize(19)
      .withPathFormat("${STREAM_NAME}/${NAMESPACE}")
      .withAccessKeyCredential("test-key", "test-secret")
      .get();

  @Test
  public void testCreateFromExistingConfig() {
    assertEquals(CONFIG, S3DestinationConfig.create(CONFIG).get());
  }

  @Test
  public void testCreateAndModify() {
    final String newBucketName = "new-bucket";
    final String newBucketPath = "new-path";
    final String newBucketRegion = "new-region";
    final String newEndpoint = "new-endpoint";
    final int newPartSize = 29;
    final String newKey = "new-key";
    final String newSecret = "new-secret";

    final S3DestinationConfig modifiedConfig = S3DestinationConfig.create(CONFIG)
        .withBucketName(newBucketName)
        .withBucketPath(newBucketPath)
        .withBucketRegion(newBucketRegion)
        .withEndpoint(newEndpoint)
        .withAccessKeyCredential(newKey, newSecret)
        .withPartSize(newPartSize)
        .get();

    assertNotEquals(CONFIG, modifiedConfig);
    assertEquals(newBucketName, modifiedConfig.getBucketName());
    assertEquals(newBucketPath, modifiedConfig.getBucketPath());
    assertEquals(newBucketRegion, modifiedConfig.getBucketRegion());
    assertEquals(newPartSize, modifiedConfig.getPartSize());

    final S3AccessKeyCredentialConfig credentialConfig = (S3AccessKeyCredentialConfig) modifiedConfig.getS3CredentialConfig();
    assertEquals(newKey, credentialConfig.getAccessKeyId());
    assertEquals(newSecret, credentialConfig.getSecretAccessKey());
  }

}
