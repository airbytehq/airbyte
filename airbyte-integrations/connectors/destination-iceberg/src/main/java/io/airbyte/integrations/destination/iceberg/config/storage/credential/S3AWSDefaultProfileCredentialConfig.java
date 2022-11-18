/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.config.storage.credential;

import com.amazonaws.auth.AWSCredentialsProvider;
import com.amazonaws.auth.DefaultAWSCredentialsProviderChain;

/**
 * @author Leibniz on 2022/10/26.
 */
public class S3AWSDefaultProfileCredentialConfig implements S3CredentialConfig {

  @Override
  public S3CredentialType getCredentialType() {
    return S3CredentialType.DEFAULT_PROFILE;
  }

  @Override
  public AWSCredentialsProvider getS3CredentialsProvider() {
    return new DefaultAWSCredentialsProviderChain();
  }

}
