/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command.s3

/**
 * Add this to your destination configuration to provide S3 client configuration.
 *
 * Currently, this is optional and only serves to enable
 * [io.airbyte.cdk.load.file.s3.S3LegacyJavaClient].
 */
interface S3ClientConfigurationProvider {
    val s3ClientConfiguration: S3ClientConfiguration
}

data class S3ClientConfiguration(val useLegacyJavaClient: Boolean = false)
