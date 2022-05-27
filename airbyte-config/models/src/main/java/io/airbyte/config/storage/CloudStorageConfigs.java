/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.storage;

import com.google.common.base.Preconditions;

/**
 * Immutable configuration for configuring Cloud storage clients. We usually allow configuring one
 * of 3 type of cloud storage clients in our env variables. We then want to opaquely pass that to
 * wherever that cloud storage is used and then, based on the configuration, spin up the correct
 * client. This configuration object allows us to do that.
 */
@SuppressWarnings("PMD.ShortMethodName")
public class CloudStorageConfigs {

  public enum WorkerStorageType {
    S3,
    MINIO,
    GCS
  }

  private final WorkerStorageType type;
  private final S3Config s3Config;
  private final MinioConfig minioConfig;
  private final GcsConfig gcsConfig;

  public static CloudStorageConfigs s3(final S3Config config) {
    return new CloudStorageConfigs(WorkerStorageType.S3, config, null, null);
  }

  public static CloudStorageConfigs minio(final MinioConfig config) {
    return new CloudStorageConfigs(WorkerStorageType.MINIO, null, config, null);
  }

  public static CloudStorageConfigs gcs(final GcsConfig config) {
    return new CloudStorageConfigs(WorkerStorageType.GCS, null, null, config);
  }

  private CloudStorageConfigs(final WorkerStorageType type,
                              final S3Config s3Config,
                              final MinioConfig minioConfig,
                              final GcsConfig gcsConfig) {
    validate(type, s3Config, minioConfig, gcsConfig);

    this.type = type;
    this.s3Config = s3Config;
    this.minioConfig = minioConfig;
    this.gcsConfig = gcsConfig;
  }

  private void validate(final WorkerStorageType type,
                        final S3Config s3Config,
                        final MinioConfig minioConfig,
                        final GcsConfig gcsConfig) {
    switch (type) {
      case S3 -> {
        Preconditions.checkNotNull(s3Config);
        Preconditions.checkArgument(minioConfig == null);
        Preconditions.checkArgument(gcsConfig == null);
      }
      case MINIO -> {
        Preconditions.checkArgument(s3Config == null);
        Preconditions.checkNotNull(minioConfig);
        Preconditions.checkArgument(gcsConfig == null);
      }
      case GCS -> {
        Preconditions.checkArgument(s3Config == null);
        Preconditions.checkArgument(minioConfig == null);
        Preconditions.checkNotNull(gcsConfig);
      }
    }
  }

  public WorkerStorageType getType() {
    return type;
  }

  public S3Config getS3Config() {
    return s3Config;
  }

  public MinioConfig getMinioConfig() {
    return minioConfig;
  }

  public GcsConfig getGcsConfig() {
    return gcsConfig;
  }

  public static class S3ApiWorkerStorageConfig {

    private final String bucketName;
    private final String awsAccessKey;
    private final String awsSecretAccessKey;

    protected S3ApiWorkerStorageConfig(final String bucketName, final String awsAccessKey, final String awsSecretAccessKey) {
      this.bucketName = bucketName;
      this.awsAccessKey = awsAccessKey;
      this.awsSecretAccessKey = awsSecretAccessKey;
    }

    public String getBucketName() {
      return bucketName;
    }

    public String getAwsAccessKey() {
      return awsAccessKey;
    }

    public String getAwsSecretAccessKey() {
      return awsSecretAccessKey;
    }

  }

  public static class S3Config extends S3ApiWorkerStorageConfig {

    private final String region;

    public S3Config(final String bucketName, final String awsAccessKey, final String awsSecretAccessKey, final String region) {
      super(bucketName, awsAccessKey, awsSecretAccessKey);
      this.region = region;
    }

    public String getRegion() {
      return region;
    }

  }

  public static class MinioConfig extends S3ApiWorkerStorageConfig {

    private final String minioEndpoint;

    public MinioConfig(final String bucketName, final String awsAccessKey, final String awsSecretAccessKey, final String minioEndpoint) {
      super(bucketName, awsAccessKey, awsSecretAccessKey);
      this.minioEndpoint = minioEndpoint;
    }

    public String getMinioEndpoint() {
      return minioEndpoint;
    }

  }

  public static class GcsConfig {

    private final String bucketName;
    private final String googleApplicationCredentials;

    public GcsConfig(final String bucketName, final String googleApplicationCredentials) {
      this.bucketName = bucketName;
      this.googleApplicationCredentials = googleApplicationCredentials;
    }

    public String getBucketName() {
      return bucketName;
    }

    public String getGoogleApplicationCredentials() {
      return googleApplicationCredentials;
    }

  }

}
