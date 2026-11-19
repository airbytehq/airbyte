/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.gcs

import com.google.auth.oauth2.ExternalAccountCredentials
import com.google.cloud.storage.Storage
import com.google.cloud.storage.StorageOptions
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.command.aws.AWSAccessKeyConfiguration
import io.airbyte.cdk.load.command.aws.AWSAccessKeyConfigurationProvider
import io.airbyte.cdk.load.command.aws.AWSArnRoleConfiguration
import io.airbyte.cdk.load.command.aws.AWSArnRoleConfigurationProvider
import io.airbyte.cdk.load.command.gcs.GOOGLE_STORAGE_ENDPOINT
import io.airbyte.cdk.load.command.gcs.GcsClientConfiguration
import io.airbyte.cdk.load.command.gcs.GcsClientConfigurationProvider
import io.airbyte.cdk.load.command.gcs.GcsHmacKeyConfiguration
import io.airbyte.cdk.load.command.gcs.GcsWorkloadIdentityFederationConfiguration
import io.airbyte.cdk.load.command.s3.S3BucketConfiguration
import io.airbyte.cdk.load.command.s3.S3BucketConfigurationProvider
import io.airbyte.cdk.load.file.s3.S3Client
import io.airbyte.cdk.load.file.s3.S3ClientFactory
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Replaces
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import java.io.ByteArrayInputStream
import java.io.IOException
import java.nio.charset.StandardCharsets

@Factory
class GcsClientFactory(
    private val gcsClientConfigurationProvider: GcsClientConfigurationProvider,
) {

    @Singleton
    @Secondary
    // We do this because we want to allow someone to supersede this client if their heart desire
    // But that at the same time we want to ensure that we always supersede the S3Client ourselves.
    @Replaces(S3Client::class)
    fun make(): GcsClient = make(gcsClientConfigurationProvider.gcsClientConfiguration)

    companion object {
        /**
         * Builds a [GcsClient] for [config] without dependency injection, e.g. from a
         * `DestinationChecker` that receives its configuration as an argument.
         * - [GcsHmacKeyConfiguration]: [GcsS3Client] over the S3-compatible XML API.
         * - [GcsWorkloadIdentityFederationConfiguration]: [GcsNativeClient] over the GCS JSON API,
         *   since the XML API cannot carry a federated token.
         */
        fun make(config: GcsClientConfiguration): GcsClient =
            when (val credential = config.credential) {
                is GcsHmacKeyConfiguration -> makeS3Client(config, credential)
                is GcsWorkloadIdentityFederationConfiguration ->
                    GcsNativeClient(makeStorage(credential), config)
            }

        private fun makeS3Client(
            config: GcsClientConfiguration,
            credential: GcsHmacKeyConfiguration,
        ): GcsClient =
            GcsS3Client(
                s3Client =
                    S3ClientFactory(
                            object : AWSArnRoleConfigurationProvider {
                                override val awsArnRoleConfiguration = AWSArnRoleConfiguration(null)
                            },
                            object : AWSAccessKeyConfigurationProvider {
                                override val awsAccessKeyConfiguration =
                                    AWSAccessKeyConfiguration(
                                        credential.accessKeyId,
                                        credential.secretAccessKey,
                                    )
                            },
                            object : S3BucketConfigurationProvider {
                                override val s3BucketConfiguration: S3BucketConfiguration =
                                    S3BucketConfiguration(
                                        s3BucketName = config.gcsBucketName,
                                        s3BucketRegion = config.region,
                                        s3Endpoint = GOOGLE_STORAGE_ENDPOINT,
                                    )
                            },
                            assumeRoleCredentials = null,
                        )
                        .make(),
                config = config,
            )

        /**
         * Builds the credentials with [ExternalAccountCredentials] rather than
         * `GoogleCredentials.fromStream`, so that only `external_account` documents are accepted
         * even if [GcsWorkloadIdentityFederationConfiguration.fromCredentialsJson] was bypassed. No
         * network call is made here; the token exchange happens on the first request.
         */
        private fun makeStorage(credential: GcsWorkloadIdentityFederationConfiguration): Storage {
            val credentials =
                try {
                    ByteArrayInputStream(
                            credential.credentialsJson.toByteArray(StandardCharsets.UTF_8),
                        )
                        .use { ExternalAccountCredentials.fromStream(it) }
                } catch (e: IOException) {
                    throw wifConfigError(e)
                } catch (e: IllegalArgumentException) {
                    throw wifConfigError(e)
                }
            return StorageOptions.newBuilder().setCredentials(credentials).build().service
        }

        private fun wifConfigError(e: Exception) =
            ConfigErrorException(
                "Could not load the Workload Identity Federation credential configuration: " +
                    (e.message ?: e::class.simpleName),
                e,
            )
    }
}
