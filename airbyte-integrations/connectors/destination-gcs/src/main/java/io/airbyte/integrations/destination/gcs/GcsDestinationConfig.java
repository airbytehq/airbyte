/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.gcs.credential.GcsCredentialConfig;
import io.airbyte.integrations.destination.gcs.credential.GcsCredentialConfigs;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.S3FormatConfig;
import io.airbyte.integrations.destination.s3.S3FormatConfigs;

public class GcsDestinationConfig extends S3DestinationConfig {

  private final GcsCredentialConfig credentialConfig;

  public GcsDestinationConfig(final String bucketName,
                              final String bucketPath,
                              final String bucketRegion,
                              final GcsCredentialConfig credentialConfig,
                              final S3FormatConfig formatConfig) {
    super(null, bucketName, bucketPath, bucketRegion, null, null, formatConfig);
    this.credentialConfig = credentialConfig;
  }

  public static GcsDestinationConfig getGcsDestinationConfig(final JsonNode config) {
    return new GcsDestinationConfig(
        config.get("gcs_bucket_name").asText(),
        config.get("gcs_bucket_path").asText(),
        config.get("gcs_bucket_region").asText(),
        GcsCredentialConfigs.getCredentialConfig(config),
        S3FormatConfigs.getS3FormatConfig(config));
  }

  public GcsCredentialConfig getCredentialConfig() {
    return credentialConfig;
  }

}
