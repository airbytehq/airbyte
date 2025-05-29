/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3.credential

enum class S3CredentialType {
    ACCESS_KEY,
    DEFAULT_PROFILE,
    ASSUME_ROLE
}
