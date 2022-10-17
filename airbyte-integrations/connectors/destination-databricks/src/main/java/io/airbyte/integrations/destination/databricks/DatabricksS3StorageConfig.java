/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.constant.S3Constants;
import io.airbyte.integrations.destination.s3.parquet.S3ParquetFormatConfig;

public class DatabricksS3StorageConfig extends DatabricksStorageConfig {

  private final S3DestinationConfig s3Config;

  public DatabricksS3StorageConfig(JsonNode config) {
    final S3DestinationConfig.Builder builder = S3DestinationConfig.create(
        config.get(S3Constants.S_3_BUCKET_NAME).asText(),
        config.get(S3Constants.S_3_BUCKET_PATH).asText(),
        config.get(S3Constants.S_3_BUCKET_REGION).asText())
        .withAccessKeyCredential(
            config.get(S3Constants.S_3_ACCESS_KEY_ID).asText(),
            config.get(S3Constants.S_3_SECRET_ACCESS_KEY).asText())
        .withFormatConfig(new S3ParquetFormatConfig(new ObjectMapper().createObjectNode()));
    if (config.has(S3Constants.FILE_NAME_PATTERN)) {
      builder.withFileNamePattern(config.get(S3Constants.FILE_NAME_PATTERN).asText());
    }
    this.s3Config = builder.get();
  }

  @Override
  public S3DestinationConfig getS3DestinationConfigOrThrow() {
    return s3Config;
  }

}
