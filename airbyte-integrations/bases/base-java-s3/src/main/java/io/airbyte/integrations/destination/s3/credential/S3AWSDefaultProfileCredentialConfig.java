/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.credential;

import com.amazonaws.auth.AWSCredentialsProvider;
import com.amazonaws.auth.AWSCredentialsProviderChain;
import com.amazonaws.auth.EC2ContainerCredentialsProviderWrapper;
import com.amazonaws.auth.EnvironmentVariableCredentialsProvider;
import com.amazonaws.auth.SystemPropertiesCredentialsProvider;
import com.amazonaws.auth.WebIdentityTokenCredentialsProvider;
import com.amazonaws.auth.profile.ProfileCredentialsProvider;
import com.amazonaws.auth.InstanceProfileCredentialsProvider;

public class S3AWSDefaultProfileCredentialConfig implements S3CredentialConfig {

  @Override
  public S3CredentialType getCredentialType() {
    return S3CredentialType.DEFAULT_PROFILE;
  }

  @Override
  public AWSCredentialsProvider getS3CredentialsProvider() {
    return new AWSCredentialsProviderChain(
            WebIdentityTokenCredentialsProvider.create(),
            new SystemPropertiesCredentialsProvider(),
            new ProfileCredentialsProvider(),
            new EC2ContainerCredentialsProviderWrapper(),
            new InstanceProfileCredentialsProvider(),
            new EnvironmentVariableCredentialsProvider());
  }

}
