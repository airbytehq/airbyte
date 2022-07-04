/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import com.amazonaws.ClientConfiguration;
import com.amazonaws.auth.AWSCredentialsProvider;
import com.amazonaws.client.builder.AwsClientBuilder;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.s3.credential.S3AccessKeyCredentialConfig;
import io.airbyte.integrations.destination.s3.credential.S3CredentialConfig;
import io.airbyte.integrations.destination.s3.credential.S3CredentialType;
import io.airbyte.integrations.destination.s3.credential.S3AWSDefaultProfileCredentialConfig;
import java.util.Objects;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * An S3 configuration. Typical usage sets at most one of {@code bucketPath} (necessary for more
 * delicate data syncing to S3)
 */
public class S3DestinationConfig {

  private static final Logger LOGGER = LoggerFactory.getLogger(S3DestinationConfig.class);

  private final String endpoint;
  private final String bucketName;
  private final String bucketPath;
  private final String bucketRegion;
  private final String pathFormat;
  private final S3CredentialConfig credentialConfig;
  private final S3FormatConfig formatConfig;

  private final Object lock = new Object();
  private AmazonS3 s3Client;

  public S3DestinationConfig(final String endpoint,
                             final String bucketName,
                             final String bucketPath,
                             final String bucketRegion,
                             final String pathFormat,
                             final S3CredentialConfig credentialConfig,
                             final S3FormatConfig formatConfig,
                             final AmazonS3 s3Client) {
    this.endpoint = endpoint;
    this.bucketName = bucketName;
    this.bucketPath = bucketPath;
    this.bucketRegion = bucketRegion;
    this.pathFormat = pathFormat;
    this.credentialConfig = credentialConfig;
    this.formatConfig = formatConfig;
    this.s3Client = s3Client;
  }

  public static Builder create(final String bucketName, final String bucketPath, final String bucketRegion) {
    return new Builder(bucketName, bucketPath, bucketRegion);
  }

  public static Builder create(final S3DestinationConfig config) {
    return new Builder(config.getBucketName(), config.getBucketPath(), config.getBucketRegion())
        .withEndpoint(config.getEndpoint())
        .withCredentialConfig(config.getS3CredentialConfig())
        .withFormatConfig(config.getFormatConfig());
  }

  public static S3DestinationConfig getS3DestinationConfig(final JsonNode config) {
    Builder builder = S3DestinationConfig.create(
        config.get("s3_bucket_name").asText(),
        "",
        config.get("s3_bucket_region").asText());

    if (config.has("s3_bucket_path")) {
      builder = builder.withBucketPath(config.get("s3_bucket_path").asText());
    }

    if (config.has("s3_path_format")) {
      builder = builder.withPathFormat(config.get("s3_path_format").asText());
    }

    if (config.has("s3_endpoint")) {
      builder = builder.withEndpoint(config.get("s3_endpoint").asText());
    }

    final S3CredentialConfig credentialConfig;
    if (config.has("access_key_id")) {
      credentialConfig = new S3AccessKeyCredentialConfig(config.get("access_key_id").asText(), config.get("secret_access_key").asText());
    } else {
      credentialConfig = new S3AWSDefaultProfileCredentialConfig();
    }
    builder = builder.withCredentialConfig(credentialConfig);

    // In the "normal" S3 destination, this is never null. However, the Redshift and Snowflake copy
    // destinations don't set a Format config.
    if (config.has("format")) {
      builder = builder.withFormatConfig(S3FormatConfigs.getS3FormatConfig(config));
    }

    return builder.get();
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

  public String getPathFormat() {
    return pathFormat;
  }

  public String getBucketRegion() {
    return bucketRegion;
  }

  public S3CredentialConfig getS3CredentialConfig() {
    return credentialConfig;
  }

  public S3FormatConfig getFormatConfig() {
    return formatConfig;
  }

  public AmazonS3 getS3Client() {
    synchronized (lock) {
      if (s3Client == null) {
        return resetS3Client();
      }
      return s3Client;
    }
  }

  public AmazonS3 resetS3Client() {
    synchronized (lock) {
      if (s3Client != null) {
        s3Client.shutdown();
      }
      s3Client = createS3Client();
      return s3Client;
    }
  }

  protected AmazonS3 createS3Client() {
    LOGGER.info("Creating S3 client...");

    final AWSCredentialsProvider credentialsProvider = credentialConfig.getS3CredentialsProvider();
    final S3CredentialType credentialType = credentialConfig.getCredentialType();

    if (credentialType == S3CredentialType.DEFAULT_PROFILE) {
      return AmazonS3ClientBuilder.standard()
          .withRegion(bucketRegion)
          .withCredentials(credentialsProvider)
          .build();
    }

    if (endpoint == null || endpoint.isEmpty()) {
      return AmazonS3ClientBuilder.standard()
          .withCredentials(credentialsProvider)
          .withRegion(bucketRegion)
          .build();
    }

    final ClientConfiguration clientConfiguration = new ClientConfiguration();
    clientConfiguration.setSignerOverride("AWSS3V4SignerType");

    return AmazonS3ClientBuilder.standard()
        .withEndpointConfiguration(new AwsClientBuilder.EndpointConfiguration(endpoint, bucketRegion))
        .withPathStyleAccessEnabled(true)
        .withClientConfiguration(clientConfiguration)
        .withCredentials(credentialsProvider)
        .build();
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
        && Objects.equals(credentialConfig, that.credentialConfig)
        && Objects.equals(formatConfig, that.formatConfig);
  }

  @Override
  public int hashCode() {
    return Objects.hash(endpoint, bucketName, bucketPath, bucketRegion, credentialConfig, formatConfig);
  }

  public static class Builder {

    private String endpoint = "";
    private String pathFormat = S3DestinationConstants.DEFAULT_PATH_FORMAT;

    private String bucketName;
    private String bucketPath;
    private String bucketRegion;
    private S3CredentialConfig credentialConfig;
    private S3FormatConfig formatConfig;
    private AmazonS3 s3Client;

    private Builder(final String bucketName, final String bucketPath, final String bucketRegion) {
      this.bucketName = bucketName;
      this.bucketPath = bucketPath;
      this.bucketRegion = bucketRegion;
    }

    public Builder withBucketName(final String bucketName) {
      this.bucketName = bucketName;
      return this;
    }

    public Builder withBucketPath(final String bucketPath) {
      this.bucketPath = bucketPath;
      return this;
    }

    public Builder withBucketRegion(final String bucketRegion) {
      this.bucketRegion = bucketRegion;
      return this;
    }

    public Builder withPathFormat(final String pathFormat) {
      this.pathFormat = pathFormat;
      return this;
    }

    public Builder withEndpoint(final String endpoint) {
      this.endpoint = endpoint;
      return this;
    }

    public Builder withFormatConfig(final S3FormatConfig formatConfig) {
      this.formatConfig = formatConfig;
      return this;
    }

    public Builder withAccessKeyCredential(final String accessKeyId, final String secretAccessKey) {
      this.credentialConfig = new S3AccessKeyCredentialConfig(accessKeyId, secretAccessKey);
      return this;
    }

    public Builder withCredentialConfig(final S3CredentialConfig credentialConfig) {
      this.credentialConfig = credentialConfig;
      return this;
    }

    public Builder withS3Client(final AmazonS3 s3Client) {
      this.s3Client = s3Client;
      return this;
    }

    public S3DestinationConfig get() {
      return new S3DestinationConfig(
          endpoint,
          bucketName,
          bucketPath,
          bucketRegion,
          pathFormat,
          credentialConfig,
          formatConfig,
          s3Client);
    }

  }

}
