/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.gcs

import com.google.auth.oauth2.AwsCredentials
import com.google.cloud.storage.StorageOptions
import io.airbyte.cdk.load.command.gcs.GcsClientConfigurationProvider
import io.airbyte.cdk.load.command.gcs.GcsHmacKeyConfiguration
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
        val credentials = config.credential as GcsHmacKeyConfiguration

        val awsCredentials =
            AwsCredentials.newBuilder()
                .setClientId(credentials.accessKeyId)
                .setClientSecret(credentials.secretAccessKey)
                .build()

        // For HMAC authentication, we use StorageOptions with AwsCredentials
        val storage = StorageOptions.newBuilder().setCredentials(awsCredentials).build().service

        return GcsClient(storage, config)
    }
}
