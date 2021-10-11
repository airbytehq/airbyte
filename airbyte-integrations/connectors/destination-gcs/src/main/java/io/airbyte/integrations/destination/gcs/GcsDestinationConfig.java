/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.gcs.credential.GcsCredentialConfig;
import io.airbyte.integrations.destination.gcs.credential.GcsCredentialConfigs;
import io.airbyte.integrations.destination.s3.S3FormatConfig;
import io.airbyte.integrations.destination.s3.S3FormatConfigs;

public class GcsDestinationConfig {

  private final String bucketName;
  private final String bucketPath;
  private final String bucketRegion;
  private final GcsCredentialConfig credentialConfig;
  private final S3FormatConfig formatConfig;

  public GcsDestinationConfig(String bucketName,
                              String bucketPath,
                              String bucketRegion,
                              GcsCredentialConfig credentialConfig,
                              S3FormatConfig formatConfig) {
    this.bucketName = bucketName;
    this.bucketPath = bucketPath;
    this.bucketRegion = bucketRegion;
    this.credentialConfig = credentialConfig;
    this.formatConfig = formatConfig;
  }

  public static GcsDestinationConfig getGcsDestinationConfig(JsonNode config) {
    return new GcsDestinationConfig(
        config.get("gcs_bucket_name").asText(),
        config.get("gcs_bucket_path").asText(),
        config.get("gcs_bucket_region").asText(),
        GcsCredentialConfigs.getCredentialConfig(config),
        S3FormatConfigs.getS3FormatConfig(config));
  }

  public String getBucketName() {
    return bucketName;
  }

  public String getBucketPath() {
    return bucketPath;
  }

  public String getBucketRegion() {
    return bucketRegion;
  }

  public GcsCredentialConfig getCredentialConfig() {
    return credentialConfig;
  }

  public S3FormatConfig getFormatConfig() {
    return formatConfig;
  }

}
