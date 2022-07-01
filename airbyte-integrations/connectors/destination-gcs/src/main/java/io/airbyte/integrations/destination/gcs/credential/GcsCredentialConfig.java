/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs.credential;

import io.airbyte.integrations.destination.s3.credential.BlobStorageCredentialConfig;
import io.airbyte.integrations.destination.s3.credential.S3CredentialConfig;
import java.util.Optional;

public interface GcsCredentialConfig extends BlobStorageCredentialConfig<GcsCredentialType> {

  Optional<S3CredentialConfig> getS3CredentialConfig();

}
