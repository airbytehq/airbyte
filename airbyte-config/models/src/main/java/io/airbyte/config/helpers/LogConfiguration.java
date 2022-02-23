/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.helpers;

/**
 * Implements {@link LogConfigs} with immutable values. Because the logging configuration overlaps
 * with other configuration, this delegation is intended to avoid multiple configurations existing
 * at once.
 */
public class LogConfiguration implements LogConfigs {

  public final static LogConfiguration EMPTY = new LogConfiguration("", "", "", "", "", "", "");

  private final String s3LogBucket;
  private final String s3LogBucketRegion;
  private final String awsAccessKey;
  private final String awsSecretAccessKey;
  private final String s3MinioEndpoint;
  private final String gcpStorageBucket;
  private final String googleApplicationCredentials;

  public LogConfiguration(final String s3LogBucket,
                          final String s3LogBucketRegion,
                          final String awsAccessKey,
                          final String awsSecretAccessKey,
                          final String s3MinioEndpoint,
                          final String gcpStorageBucket,
                          final String googleApplicationCredentials) {
    this.s3LogBucket = s3LogBucket;
    this.s3LogBucketRegion = s3LogBucketRegion;
    this.awsAccessKey = awsAccessKey;
    this.awsSecretAccessKey = awsSecretAccessKey;
    this.s3MinioEndpoint = s3MinioEndpoint;
    this.gcpStorageBucket = gcpStorageBucket;
    this.googleApplicationCredentials = googleApplicationCredentials;
  }

  @Override
  public String getS3LogBucket() {
    return s3LogBucket;
  }

  @Override
  public String getS3LogBucketRegion() {
    return s3LogBucketRegion;
  }

  @Override
  public String getAwsAccessKey() {
    return awsAccessKey;
  }

  @Override
  public String getAwsSecretAccessKey() {
    return awsSecretAccessKey;
  }

  @Override
  public String getS3MinioEndpoint() {
    return s3MinioEndpoint;
  }

  @Override
  public String getGcpStorageBucket() {
    return gcpStorageBucket;
  }

  @Override
  public String getGoogleApplicationCredentials() {
    return googleApplicationCredentials;
  }

}
