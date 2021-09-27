/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.helpers;

import io.airbyte.config.Configs;

/**
 * Implements {@link LogConfigs} by delegating to a {@link Configs} implementation. Because the
 * logging configuration overlaps with other configuration, this delegation is intended to avoid
 * multiple configurations existing at once.
 */
public class LogConfigDelegator implements LogConfigs {

  private final Configs delegate;

  public LogConfigDelegator(Configs configs) {
    delegate = configs;
  }

  @Override
  public String getS3LogBucket() {
    return delegate.getS3LogBucket();
  }

  @Override
  public String getS3LogBucketRegion() {
    return delegate.getS3LogBucketRegion();
  }

  @Override
  public String getAwsAccessKey() {
    return delegate.getAwsAccessKey();
  }

  @Override
  public String getAwsSecretAccessKey() {
    return delegate.getAwsSecretAccessKey();
  }

  @Override
  public String getS3MinioEndpoint() {
    return delegate.getS3MinioEndpoint();
  }

  @Override
  public String getGcpStorageBucket() {
    return delegate.getGcpStorageBucket();
  }

  @Override
  public String getGoogleApplicationCredentials() {
    return delegate.getGoogleApplicationCredentials();
  }

}
