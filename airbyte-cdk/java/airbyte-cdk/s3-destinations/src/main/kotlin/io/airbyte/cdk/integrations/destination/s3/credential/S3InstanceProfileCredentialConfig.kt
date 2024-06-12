/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3.credential

import com.amazonaws.auth.AWSCredentialsProvider
import com.amazonaws.auth.InstanceProfileCredentialsProvider

class S3InstanceProfileCredentialConfig : S3CredentialConfig {
    override val credentialType: S3CredentialType
        get() = S3CredentialType.DEFAULT_PROFILE

    override val s3CredentialsProvider: AWSCredentialsProvider
        get() = InstanceProfileCredentialsProvider(false)
}
