/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks;

import static org.junit.jupiter.api.Assertions.*;

import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import java.util.UUID;
import org.junit.jupiter.api.Test;

class DatabricksStreamCopierTest {

  @Test
  public void testGetStagingS3DestinationConfig() {
    String bucketPath = UUID.randomUUID().toString();
    S3DestinationConfig config = new S3DestinationConfig("", "", bucketPath, "", "", "", null);
    String stagingFolder = UUID.randomUUID().toString();
    S3DestinationConfig stagingConfig = DatabricksStreamCopier.getStagingS3DestinationConfig(config, stagingFolder);
    assertEquals(String.format("%s/%s", bucketPath, stagingFolder), stagingConfig.getBucketPath());
  }

}
