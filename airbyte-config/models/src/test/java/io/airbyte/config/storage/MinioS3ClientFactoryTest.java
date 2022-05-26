/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.storage;

import static org.junit.jupiter.api.Assertions.assertThrows;

import io.airbyte.config.storage.CloudStorageConfigs.MinioConfig;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

@SuppressWarnings("PMD.JUnitTestsShouldIncludeAssert")
class MinioS3ClientFactoryTest {

  @Test
  void testMinio() {
    final var minioConfig = Mockito.mock(MinioConfig.class);
    Mockito.when(minioConfig.getAwsAccessKey()).thenReturn("access-key");
    Mockito.when(minioConfig.getAwsSecretAccessKey()).thenReturn("access-key-secret");
    Mockito.when(minioConfig.getBucketName()).thenReturn("test-bucket");
    Mockito.when(minioConfig.getMinioEndpoint()).thenReturn("https://minio-endpoint");

    new MinioS3ClientFactory(minioConfig).get();
  }

  @Test
  void testMinioEndpointMissing() {
    final var minioConfig = Mockito.mock(MinioConfig.class);
    // Missing bucket and access key.
    Mockito.when(minioConfig.getAwsAccessKey()).thenReturn("access-key");
    Mockito.when(minioConfig.getAwsSecretAccessKey()).thenReturn("access-key-secret");
    Mockito.when(minioConfig.getBucketName()).thenReturn("test-bucket");
    Mockito.when(minioConfig.getMinioEndpoint()).thenReturn("");

    assertThrows(IllegalArgumentException.class, () -> new MinioS3ClientFactory(minioConfig));
  }

}
