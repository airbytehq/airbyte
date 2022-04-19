/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import com.amazonaws.ClientConfiguration;
import com.amazonaws.auth.AWSCredentials;
import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.auth.InstanceProfileCredentialsProvider;
import com.amazonaws.client.builder.AwsClientBuilder;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import com.fasterxml.jackson.databind.JsonNode;
import java.util.Objects;

/**
 * An S3 configuration. Typical usage sets at most one of {@code bucketPath} (necessary for more
 * delicate data syncing to S3) and {@code partSize} (used by certain bulk-load database
 * operations).
 */
public class S3DestinationConfig {

  // The smallest part size is 5MB. An S3 upload can be maximally formed of 10,000 parts. This gives
  // us an upper limit of 10,000 * 10 / 1000 = 100 GB per table with a 10MB part size limit.
  // WARNING: Too large a part size can cause potential OOM errors.
  public static final int DEFAULT_PART_SIZE_MB = 10;

  private final String endpoint;
  private final String bucketName;
  private final String bucketPath;
  private final String bucketRegion;
  private final String accessKeyId;
  private final String secretAccessKey;
  private final Integer partSize;
  private final S3FormatConfig formatConfig;

  /**
   * The part size should not matter in any use case that depends on this constructor. So the default
   * 10 MB is used.
   */
  public S3DestinationConfig(final String endpoint,
                             final String bucketName,
                             final String bucketPath,
                             final String bucketRegion,
                             final String accessKeyId,
                             final String secretAccessKey,
                             final S3FormatConfig formatConfig) {
    this(endpoint, bucketName, bucketPath, bucketRegion, accessKeyId, secretAccessKey, DEFAULT_PART_SIZE_MB, formatConfig);
  }

  public S3DestinationConfig(final String endpoint,
                             final String bucketName,
                             final String bucketPath,
                             final String bucketRegion,
                             final String accessKeyId,
                             final String secretAccessKey,
                             final Integer partSize,
                             final S3FormatConfig formatConfig) {
    this.endpoint = endpoint;
    this.bucketName = bucketName;
    this.bucketPath = bucketPath;
    this.bucketRegion = bucketRegion;
    this.accessKeyId = accessKeyId;
    this.secretAccessKey = secretAccessKey;
    this.formatConfig = formatConfig;
    this.partSize = partSize;
  }

  public static S3DestinationConfig getS3DestinationConfig(final JsonNode config) {
    var partSize = DEFAULT_PART_SIZE_MB;
    if (config.get("part_size") != null) {
      partSize = config.get("part_size").asInt();
    }
    String bucketPath = null;
    if (config.get("s3_bucket_path") != null) {
      bucketPath = config.get("s3_bucket_path").asText();
    }
    // In the "normal" S3 destination, this is never null. However, the Redshift and Snowflake copy
    // destinations don't set a Format config.
    S3FormatConfig format = null;
    if (config.get("format") != null) {
      format = S3FormatConfigs.getS3FormatConfig(config);
    }
    return new S3DestinationConfig(
        config.get("s3_endpoint") == null ? "" : config.get("s3_endpoint").asText(),
        config.get("s3_bucket_name").asText(),
        bucketPath,
        config.get("s3_bucket_region").asText(),
        config.get("access_key_id") == null ? "" : config.get("access_key_id").asText(),
        config.get("secret_access_key") == null ? "" : config.get("secret_access_key").asText(),
        partSize,
        format);
  }

  public String getEndpoint() {
    return endpoint;
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

  public String getAccessKeyId() {
    return accessKeyId;
  }

  public String getSecretAccessKey() {
    return secretAccessKey;
  }

  public Integer getPartSize() {
    return partSize;
  }

  public S3FormatConfig getFormatConfig() {
    return formatConfig;
  }

  public AmazonS3 getS3Client() {
    final AWSCredentials awsCreds = new BasicAWSCredentials(accessKeyId, secretAccessKey);

    if (accessKeyId.isEmpty() && !secretAccessKey.isEmpty()
        || !accessKeyId.isEmpty() && secretAccessKey.isEmpty()) {
      throw new RuntimeException("Either both accessKeyId and secretAccessKey should be provided, or neither");
    }

    if (accessKeyId.isEmpty() && secretAccessKey.isEmpty()) {
      return AmazonS3ClientBuilder.standard()
          .withCredentials(new InstanceProfileCredentialsProvider(false))
          .build();
    }

    else if (endpoint == null || endpoint.isEmpty()) {
      return AmazonS3ClientBuilder.standard()
          .withCredentials(new AWSStaticCredentialsProvider(awsCreds))
          .withRegion(bucketRegion)
          .build();
    }

    final ClientConfiguration clientConfiguration = new ClientConfiguration();
    clientConfiguration.setSignerOverride("AWSS3V4SignerType");

    return AmazonS3ClientBuilder
        .standard()
        .withEndpointConfiguration(new AwsClientBuilder.EndpointConfiguration(endpoint, bucketRegion))
        .withPathStyleAccessEnabled(true)
        .withClientConfiguration(clientConfiguration)
        .withCredentials(new AWSStaticCredentialsProvider(awsCreds))
        .build();
  }

  public S3DestinationConfig cloneWithFormatConfig(final S3FormatConfig formatConfig) {
    return new S3DestinationConfig(
        this.endpoint,
        this.bucketName,
        this.bucketPath,
        this.bucketRegion,
        this.accessKeyId,
        this.secretAccessKey,
        this.partSize,
        formatConfig);
  }

  @Override
  public boolean equals(final Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    final S3DestinationConfig that = (S3DestinationConfig) o;
    return Objects.equals(endpoint, that.endpoint) && Objects.equals(bucketName, that.bucketName) && Objects.equals(
        bucketPath, that.bucketPath) && Objects.equals(bucketRegion, that.bucketRegion)
        && Objects.equals(accessKeyId,
            that.accessKeyId)
        && Objects.equals(secretAccessKey, that.secretAccessKey) && Objects.equals(partSize, that.partSize)
        && Objects.equals(formatConfig, that.formatConfig);
  }

  @Override
  public int hashCode() {
    return Objects.hash(endpoint, bucketName, bucketPath, bucketRegion, accessKeyId, secretAccessKey, partSize, formatConfig);
  }

}
