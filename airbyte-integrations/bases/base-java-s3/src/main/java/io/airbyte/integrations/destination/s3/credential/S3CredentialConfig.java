/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.credential;

import com.amazonaws.auth.AWSCredentialsProvider;

public interface S3CredentialConfig extends BlobStorageCredentialConfig<S3CredentialType> {

  AWSCredentialsProvider getS3CredentialsProvider();

}
