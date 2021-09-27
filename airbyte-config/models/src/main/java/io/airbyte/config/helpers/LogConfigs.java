/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.helpers;

/**
 * Configuration required to retrieve logs. This is a subset of the methods defined in
 * {@link io.airbyte.config.Configs} so actual look up can be delegated in
 * {@link LogConfigDelegator}. This prevents conflicting configuration existing at once.
 */
public interface LogConfigs {

  String getS3LogBucket();

  String getS3LogBucketRegion();

  String getAwsAccessKey();

  String getAwsSecretAccessKey();

  String getS3MinioEndpoint();

  String getGcpStorageBucket();

  String getGoogleApplicationCredentials();

}
