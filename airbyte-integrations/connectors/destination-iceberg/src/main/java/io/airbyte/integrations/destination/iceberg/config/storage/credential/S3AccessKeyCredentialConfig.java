/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.config.storage.credential;

import com.amazonaws.auth.AWSCredentials;
import com.amazonaws.auth.AWSCredentialsProvider;
import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.BasicAWSCredentials;

/**
 * @author Leibniz on 2022/10/26.
 */
public class S3AccessKeyCredentialConfig implements S3CredentialConfig {

  private final String accessKeyId;
  private final String secretAccessKey;

  public S3AccessKeyCredentialConfig(final String accessKeyId, final String secretAccessKey) {
    this.accessKeyId = accessKeyId;
    this.secretAccessKey = secretAccessKey;
  }

  @Override
  public S3CredentialType getCredentialType() {
    return S3CredentialType.ACCESS_KEY;
  }

  @Override
  public AWSCredentialsProvider getS3CredentialsProvider() {
    final AWSCredentials awsCreds = new BasicAWSCredentials(accessKeyId, secretAccessKey);
    return new AWSStaticCredentialsProvider(awsCreds);
  }

  public String getAccessKeyId() {
    return accessKeyId;
  }

  public String getSecretAccessKey() {
    return secretAccessKey;
  }

}
