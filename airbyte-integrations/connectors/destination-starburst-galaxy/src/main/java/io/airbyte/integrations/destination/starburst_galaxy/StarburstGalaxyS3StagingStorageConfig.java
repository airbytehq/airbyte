/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starburst_galaxy;

import static io.airbyte.integrations.destination.s3.constant.S3Constants.S_3_ACCESS_KEY_ID;
import static io.airbyte.integrations.destination.s3.constant.S3Constants.S_3_BUCKET_NAME;
import static io.airbyte.integrations.destination.s3.constant.S3Constants.S_3_BUCKET_PATH;
import static io.airbyte.integrations.destination.s3.constant.S3Constants.S_3_BUCKET_REGION;
import static io.airbyte.integrations.destination.s3.constant.S3Constants.S_3_SECRET_ACCESS_KEY;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.parquet.S3ParquetFormatConfig;

public class StarburstGalaxyS3StagingStorageConfig
    extends StarburstGalaxyStagingStorageConfig {

  private final S3DestinationConfig s3Config;

  public StarburstGalaxyS3StagingStorageConfig(JsonNode config) {
    final S3DestinationConfig.Builder builder = S3DestinationConfig.create(
        config.get(S_3_BUCKET_NAME).asText(),
        config.get(S_3_BUCKET_PATH).asText(),
        config.get(S_3_BUCKET_REGION).asText())
        .withAccessKeyCredential(
            config.get(S_3_ACCESS_KEY_ID).asText(),
            config.get(S_3_SECRET_ACCESS_KEY).asText())
        .withFormatConfig(new S3ParquetFormatConfig(new ObjectMapper().createObjectNode()));
    this.s3Config = builder.get();
  }

  @Override
  public S3DestinationConfig getS3DestinationConfigOrThrow() {
    return s3Config;
  }

}
