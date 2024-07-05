/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3.credential

import com.amazonaws.auth.AWSCredentialsProvider

interface S3CredentialConfig {
    val s3CredentialsProvider: AWSCredentialsProvider
    val credentialType: S3CredentialType
}
