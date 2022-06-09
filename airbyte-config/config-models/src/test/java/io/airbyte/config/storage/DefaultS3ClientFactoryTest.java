/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.storage;

import static org.junit.jupiter.api.Assertions.assertThrows;

import io.airbyte.config.storage.CloudStorageConfigs.S3Config;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

@SuppressWarnings("PMD.JUnitTestsShouldIncludeAssert")
class DefaultS3ClientFactoryTest {

  @Test
  void testS3() {
    final var s3Config = Mockito.mock(S3Config.class);
    Mockito.when(s3Config.getAwsAccessKey()).thenReturn("access-key");
    Mockito.when(s3Config.getAwsSecretAccessKey()).thenReturn("access-key-secret");
    Mockito.when(s3Config.getBucketName()).thenReturn("test-bucket");
    Mockito.when(s3Config.getRegion()).thenReturn("us-east-1");

    new DefaultS3ClientFactory(s3Config).get();
  }

  @Test
  void testS3RegionNotSet() {
    final var s3Config = Mockito.mock(S3Config.class);
    // Missing bucket and access key.
    Mockito.when(s3Config.getAwsAccessKey()).thenReturn("");
    Mockito.when(s3Config.getAwsSecretAccessKey()).thenReturn("access-key-secret");
    Mockito.when(s3Config.getBucketName()).thenReturn("");
    Mockito.when(s3Config.getRegion()).thenReturn("");

    assertThrows(IllegalArgumentException.class, () -> new DefaultS3ClientFactory(s3Config));
  }

}
