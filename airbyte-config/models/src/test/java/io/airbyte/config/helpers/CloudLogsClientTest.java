/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.helpers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

public class CloudLogsClientTest {

  @Nested
  class CloudLogClientMissingConfiguration {

    @Test
    public void testMinio() {
      var configs = Mockito.mock(LogConfigs.class);
      // Mising bucket.
      Mockito.when(configs.getS3MinioEndpoint()).thenReturn("minio-endpoint");
      Mockito.when(configs.getAwsAccessKey()).thenReturn("access-key");
      Mockito.when(configs.getAwsSecretAccessKey()).thenReturn("access-key-secret");
      Mockito.when(configs.getS3LogBucket()).thenReturn("");
      Mockito.when(configs.getS3LogBucketRegion()).thenReturn("");

      assertThrows(RuntimeException.class, () -> CloudLogs.createCloudLogClient(configs));
    }

    @Test
    public void testAws() {
      var configs = Mockito.mock(LogConfigs.class);
      // Missing bucket and access key.
      Mockito.when(configs.getS3MinioEndpoint()).thenReturn("");
      Mockito.when(configs.getAwsAccessKey()).thenReturn("");
      Mockito.when(configs.getAwsSecretAccessKey()).thenReturn("access-key-secret");
      Mockito.when(configs.getS3LogBucket()).thenReturn("");
      Mockito.when(configs.getS3LogBucketRegion()).thenReturn("");

      assertThrows(RuntimeException.class, () -> CloudLogs.createCloudLogClient(configs));
    }

    @Test
    public void testGcs() {
      var configs = Mockito.mock(LogConfigs.class);
      Mockito.when(configs.getAwsAccessKey()).thenReturn("");
      Mockito.when(configs.getAwsSecretAccessKey()).thenReturn("");
      Mockito.when(configs.getS3LogBucket()).thenReturn("");
      Mockito.when(configs.getS3LogBucketRegion()).thenReturn("");

      // Missing bucket.
      Mockito.when(configs.getGcpStorageBucket()).thenReturn("");
      Mockito.when(configs.getGoogleApplicationCredentials()).thenReturn("path/to/google/secret");

      assertThrows(RuntimeException.class, () -> CloudLogs.createCloudLogClient(configs));
    }

  }

  @Test
  public void createCloudLogClientTestMinio() {
    var configs = Mockito.mock(LogConfigs.class);
    Mockito.when(configs.getS3MinioEndpoint()).thenReturn("minio-endpoint");
    Mockito.when(configs.getAwsAccessKey()).thenReturn("access-key");
    Mockito.when(configs.getAwsSecretAccessKey()).thenReturn("access-key-secret");
    Mockito.when(configs.getS3LogBucket()).thenReturn("test-bucket");
    Mockito.when(configs.getS3LogBucketRegion()).thenReturn("");

    assertEquals(S3Logs.class, CloudLogs.createCloudLogClient(configs).getClass());
  }

  @Test
  public void createCloudLogClientTestAws() {
    var configs = Mockito.mock(LogConfigs.class);
    Mockito.when(configs.getS3MinioEndpoint()).thenReturn("");
    Mockito.when(configs.getAwsAccessKey()).thenReturn("access-key");
    Mockito.when(configs.getAwsSecretAccessKey()).thenReturn("access-key-secret");
    Mockito.when(configs.getS3LogBucket()).thenReturn("test-bucket");
    Mockito.when(configs.getS3LogBucketRegion()).thenReturn("us-east-1");

    assertEquals(S3Logs.class, CloudLogs.createCloudLogClient(configs).getClass());
  }

  @Test
  public void createCloudLogClientTestGcs() {
    var configs = Mockito.mock(LogConfigs.class);
    Mockito.when(configs.getAwsAccessKey()).thenReturn("");
    Mockito.when(configs.getAwsSecretAccessKey()).thenReturn("");
    Mockito.when(configs.getS3LogBucket()).thenReturn("");
    Mockito.when(configs.getS3LogBucketRegion()).thenReturn("");

    Mockito.when(configs.getGcpStorageBucket()).thenReturn("storage-bucket");
    Mockito.when(configs.getGoogleApplicationCredentials()).thenReturn("path/to/google/secret");

    assertEquals(GcsLogs.class, CloudLogs.createCloudLogClient(configs).getClass());
  }

}
