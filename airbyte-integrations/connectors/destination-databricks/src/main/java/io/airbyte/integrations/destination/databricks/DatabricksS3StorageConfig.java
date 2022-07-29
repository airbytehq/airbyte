/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;

public class DatabricksS3StorageConfig extends DatabricksStorageConfig {

  private final S3DestinationConfig s3Config;

  public DatabricksS3StorageConfig(JsonNode config) {
    this.s3Config = S3DestinationConfig.getS3DestinationConfig(config);
  }

  @Override
  public S3DestinationConfig getS3DestinationConfigOrThrow() {
    return s3Config;
  }

}
