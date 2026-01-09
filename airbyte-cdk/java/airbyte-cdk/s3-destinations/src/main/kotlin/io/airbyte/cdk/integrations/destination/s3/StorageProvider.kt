/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3

/** Represents storage provider type */
enum class StorageProvider {
    AWS_S3,
    CF_R2
}
