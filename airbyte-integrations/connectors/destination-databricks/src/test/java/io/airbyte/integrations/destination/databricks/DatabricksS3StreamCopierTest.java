/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import java.util.UUID;
import org.junit.jupiter.api.Test;

class DatabricksS3StreamCopierTest {

  @Test
  public void testGetStagingS3DestinationConfig() {
    final String bucketPath = UUID.randomUUID().toString();
    final S3DestinationConfig config = S3DestinationConfig.create("", bucketPath, "").get();
    final String stagingFolder = UUID.randomUUID().toString();
    final S3DestinationConfig stagingConfig = DatabricksS3StreamCopier.getStagingS3DestinationConfig(config, stagingFolder);
    assertEquals(String.format("%s/%s", bucketPath, stagingFolder), stagingConfig.getBucketPath());
  }

}
