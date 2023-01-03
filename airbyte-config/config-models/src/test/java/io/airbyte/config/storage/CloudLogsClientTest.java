/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.storage;

import static org.junit.jupiter.api.Assertions.assertThrows;

import io.airbyte.config.storage.CloudStorageConfigs.GcsConfig;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

@SuppressWarnings("PMD.JUnitTestsShouldIncludeAssert")
class CloudLogsClientTest {

  @Test
  void testGcsMissingBucket() {
    final var configs = Mockito.mock(GcsConfig.class);
    Mockito.when(configs.getBucketName()).thenReturn("");
    Mockito.when(configs.getGoogleApplicationCredentials()).thenReturn("path/to/google/secret");

    assertThrows(RuntimeException.class, () -> new DefaultGcsClientFactory(configs));
  }

  @Test
  void testGcs() {
    final var configs = Mockito.mock(GcsConfig.class);
    Mockito.when(configs.getBucketName()).thenReturn("storage-bucket");
    Mockito.when(configs.getGoogleApplicationCredentials()).thenReturn("path/to/google/secret");

    new DefaultGcsClientFactory(configs);
  }

}
