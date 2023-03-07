/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.config.storage.credential;

import com.amazonaws.auth.AWSCredentialsProvider;

/**
 * @author Leibniz on 2022/10/26.
 */
public interface S3CredentialConfig {

  S3CredentialType getCredentialType();

  AWSCredentialsProvider getS3CredentialsProvider();

}
