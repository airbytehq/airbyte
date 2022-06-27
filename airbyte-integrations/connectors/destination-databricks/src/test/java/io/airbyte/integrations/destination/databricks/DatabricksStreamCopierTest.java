/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks;

import static org.junit.jupiter.api.Assertions.*;

import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import java.util.UUID;
import org.junit.jupiter.api.Test;

class DatabricksStreamCopierTest {

  @Test
  public void testGetStagingS3DestinationConfig() {
    final String bucketPath = UUID.randomUUID().toString();
    final S3DestinationConfig config = S3DestinationConfig.create("", bucketPath, "").get();
    final String stagingFolder = UUID.randomUUID().toString();
    final S3DestinationConfig stagingConfig = DatabricksStreamCopier.getStagingS3DestinationConfig(config, stagingFolder);
    assertEquals(String.format("%s/%s", bucketPath, stagingFolder), stagingConfig.getBucketPath());
  }

}
