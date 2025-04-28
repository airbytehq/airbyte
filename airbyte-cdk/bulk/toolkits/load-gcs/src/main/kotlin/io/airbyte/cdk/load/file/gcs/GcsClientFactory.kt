/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.gcs

import io.airbyte.cdk.load.command.aws.AWSAccessKeyConfiguration
import io.airbyte.cdk.load.command.aws.AWSAccessKeyConfigurationProvider
import io.airbyte.cdk.load.command.aws.AWSArnRoleConfiguration
import io.airbyte.cdk.load.command.aws.AWSArnRoleConfigurationProvider
import io.airbyte.cdk.load.command.gcs.GOOGLE_STORAGE_ENDPOINT
import io.airbyte.cdk.load.command.gcs.GcsClientConfigurationProvider
import io.airbyte.cdk.load.command.gcs.GcsHmacKeyConfiguration
import io.airbyte.cdk.load.command.s3.S3BucketConfiguration
import io.airbyte.cdk.load.command.s3.S3BucketConfigurationProvider
import io.airbyte.cdk.load.file.s3.S3Client
import io.airbyte.cdk.load.file.s3.S3ClientFactory
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Replaces
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

@Factory
class GcsClientFactory(
    private val gcsClientConfigurationProvider: GcsClientConfigurationProvider,
) {

    @Singleton
    @Secondary
    // We do this because we want to allow someone to supersede this client if their heart desire
    // But that at the same time we want to ensure that we always supersede the S3Client ourselves.
    @Replaces(S3Client::class)
    fun make(): GcsClient {
        val config = gcsClientConfigurationProvider.gcsClientConfiguration

        return when (config.credential) {
            is GcsHmacKeyConfiguration -> {
                GcsS3Client(
                    s3Client =
                        S3ClientFactory(
                                object : AWSArnRoleConfigurationProvider {
                                    override val awsArnRoleConfiguration =
                                        AWSArnRoleConfiguration(null)
                                },
                                object : AWSAccessKeyConfigurationProvider {
                                    override val awsAccessKeyConfiguration =
                                        AWSAccessKeyConfiguration(
                                            config.credential.accessKeyId,
                                            config.credential.secretAccessKey,
                                        )
                                },
                                object : S3BucketConfigurationProvider {
                                    override val s3BucketConfiguration: S3BucketConfiguration =
                                        S3BucketConfiguration(
                                            s3BucketName = config.gcsBucketName,
                                            s3BucketRegion = config.region,
                                            s3Endpoint = GOOGLE_STORAGE_ENDPOINT
                                        )
                                },
                                assumeRoleCredentials = null,
                                null
                            )
                            .make(),
                    config = config,
                )
            }
        //            else -> {
        //                // This branch is never executed, because there's no alternative to HMAC
        // auth.
        //                // But this is approximately what we would do.
        //                val storage =
        // StorageOptions.newBuilder().setCredentials(TODO()).build().service
        //                return GcsNativeClient(storage, config)
        //            }
        }
    }
}
