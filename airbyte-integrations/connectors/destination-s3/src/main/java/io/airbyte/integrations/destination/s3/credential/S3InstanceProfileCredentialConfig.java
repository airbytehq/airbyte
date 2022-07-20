/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.credential;

import com.amazonaws.auth.AWSCredentialsProvider;
import com.amazonaws.auth.InstanceProfileCredentialsProvider;

public class S3InstanceProfileCredentialConfig implements S3CredentialConfig {

  @Override
  public S3CredentialType getCredentialType() {
    return S3CredentialType.DEFAULT_PROFILE;
  }

  @Override
  public AWSCredentialsProvider getS3CredentialsProvider() {
    return new InstanceProfileCredentialsProvider(false);
  }

}
