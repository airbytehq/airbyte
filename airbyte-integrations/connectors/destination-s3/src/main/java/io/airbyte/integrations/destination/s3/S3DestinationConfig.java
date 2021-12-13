/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import com.amazonaws.ClientConfiguration;
import com.amazonaws.auth.AWSCredentials;
import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.client.builder.AwsClientBuilder;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import com.fasterxml.jackson.databind.JsonNode;
import javax.annotation.Nullable;

/**
 * An S3 configuration. Typical usage sets at most one of {@code bucketPath} (necessary for more delicate data syncing to S3) and {@code partSize}
 * (used by certain bulk-load database operations).
 */
public record S3DestinationConfig(
    String endpoint,
    String bucketName,
    String bucketPath,
    String bucketRegion,
    String accessKeyId,
    String secretAccessKey,
    Integer partSize,
    S3FormatConfig formatConfig
) {

  // The smallest part size is 5MB. An S3 upload can be maximally formed of 10,000 parts. This gives
  // us an upper limit of 10,000 * 10 / 1000 = 100 GB per table with a 10MB part size limit.
  // WARNING: Too large a part size can cause potential OOM errors.
  public static final int DEFAULT_PART_SIZE_MB = 10;

  /**
   * The part size should not matter in any use case that depends on this constructor. So the default 10 MB is used.
   */
  public S3DestinationConfig(
      final String endpoint,
      final String bucketName,
      @Nullable final String bucketPath,
      final String bucketRegion,
      final String accessKeyId,
      final String secretAccessKey,
      @Nullable final S3FormatConfig formatConfig) {
    this(endpoint, bucketName, bucketPath, bucketRegion, accessKeyId, secretAccessKey, DEFAULT_PART_SIZE_MB, formatConfig);
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
    // In the "normal" S3 destination, this is never null. However, the Redshift and Snowflake copy destinations don't set a Format config.
    S3FormatConfig format = null;
    if (config.get("format") != null) {
      format = S3FormatConfigs.getS3FormatConfig(config);
    }
    return new S3DestinationConfig(
        config.get("s3_endpoint") == null ? "" : config.get("s3_endpoint").asText(),
        config.get("s3_bucket_name").asText(),
        bucketPath,
        config.get("s3_bucket_region").asText(),
        config.get("access_key_id").asText(),
        config.get("secret_access_key").asText(),
        partSize,
        format
    );
  }

  public AmazonS3 getS3Client() {
    final AWSCredentials awsCreds = new BasicAWSCredentials(accessKeyId, secretAccessKey);

    if (endpoint == null || endpoint.isEmpty()) {
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
}
