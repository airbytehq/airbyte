/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.jdbc.copy.s3;

import com.fasterxml.jackson.databind.JsonNode;

public class S3Config {

  private final String endpoint;
  private final String bucketName;
  private final String accessKeyId;
  private final String secretAccessKey;
  private final String region;
  private final Integer partSize;

  public S3Config(String endpoint, String bucketName, String accessKeyId, String secretAccessKey, String region, Integer partSize) {
    this.endpoint = endpoint;
    this.bucketName = bucketName;
    this.accessKeyId = accessKeyId;
    this.secretAccessKey = secretAccessKey;
    this.region = region;
    this.partSize = partSize;
  }

  public String getEndpoint() {
    return endpoint;
  }

  public String getBucketName() {
    return bucketName;
  }

  public String getAccessKeyId() {
    return accessKeyId;
  }

  public String getSecretAccessKey() {
    return secretAccessKey;
  }

  public String getRegion() {
    return region;
  }

  public Integer getPartSize() {
    return partSize;
  }

  public static S3Config getS3Config(JsonNode config) {
    var partSize = S3StreamCopier.DEFAULT_PART_SIZE_MB;
    if (config.get("part_size") != null) {
      partSize = config.get("part_size").asInt();
    }
    return new S3Config(
        config.get("s3_endpoint") == null ? "" : config.get("s3_endpoint").asText(),
        config.get("s3_bucket_name").asText(),
        config.get("access_key_id").asText(),
        config.get("secret_access_key").asText(),
        config.get("s3_bucket_region").asText(),
        partSize);
  }

}
