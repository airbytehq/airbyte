package io.airbyte.integrations.destination.s3.credential;

public interface BlobStorageCredentialConfig<CredentialType> {

  CredentialType getCredentialType();

}
