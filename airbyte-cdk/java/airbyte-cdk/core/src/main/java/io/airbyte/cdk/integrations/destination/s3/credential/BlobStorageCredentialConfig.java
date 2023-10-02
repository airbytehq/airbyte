/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3.credential;

public interface BlobStorageCredentialConfig<CredentialType> {

  CredentialType getCredentialType();

}
