/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.gcs

import com.google.auth.oauth2.AwsCredentials
import com.google.cloud.storage.StorageOptions
import io.airbyte.cdk.load.command.gcs.GcsClientConfigurationProvider
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

@Factory
class GcsClientFactory(
    private val gcsClientConfigurationProvider: GcsClientConfigurationProvider,
) {

    @Singleton
    @Secondary
    fun make(): GcsClient {
        val config = gcsClientConfigurationProvider.gcsClientConfiguration

        // For HMAC authentication, we use StorageOptions with AwsCredentials
        val storage =
            StorageOptions.newBuilder()
                .setProjectId(config.projectId)
                .setCredentials(AwsCredentials.create(config.hmacKeyAccessId, config.hmacKeySecret))
                .build()
                .service

        return GcsClient(storage, config)
    }
}
