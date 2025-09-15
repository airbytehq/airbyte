/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.gcs.credential

import io.airbyte.cdk.integrations.destination.s3.credential.BlobStorageCredentialConfig
import io.airbyte.cdk.integrations.destination.s3.credential.S3CredentialConfig
import java.util.*

interface GcsCredentialConfig : BlobStorageCredentialConfig<GcsCredentialType> {
    val s3CredentialConfig: Optional<S3CredentialConfig>
}
