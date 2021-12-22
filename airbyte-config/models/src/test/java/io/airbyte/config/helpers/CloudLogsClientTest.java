/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.helpers;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.config.storage.CloudStorageConfigs;
import io.airbyte.config.storage.CloudStorageConfigs.GcsConfig;
import io.airbyte.config.storage.CloudStorageConfigs.MinioConfig;
import io.airbyte.config.storage.CloudStorageConfigs.S3Config;
import org.junit.jupiter.api.Test;

public class CloudLogsClientTest {

  @Test
  public void createCloudLogClientTestMinio() {
    final var configs = new LogConfigs(CloudStorageConfigs.minio(new MinioConfig(
        "test-bucket",
        "access-key",
        "access-key-secret",
        "minio-endpoint")));

    assertEquals(S3Logs.class, CloudLogs.createCloudLogClient(configs).getClass());
  }

  @Test
  public void createCloudLogClientTestAws() {
    final var configs = new LogConfigs(CloudStorageConfigs.s3(new S3Config(
        "test-bucket",
        "access-key",
        "access-key-secret",
        "us-east-1")));

    assertEquals(S3Logs.class, CloudLogs.createCloudLogClient(configs).getClass());
  }

  @Test
  public void createCloudLogClientTestGcs() {
    final var configs = new LogConfigs(CloudStorageConfigs.gcs(new GcsConfig(
        "storage-bucket",
        "path/to/google/secret")));

    assertEquals(GcsLogs.class, CloudLogs.createCloudLogClient(configs).getClass());
  }

}
