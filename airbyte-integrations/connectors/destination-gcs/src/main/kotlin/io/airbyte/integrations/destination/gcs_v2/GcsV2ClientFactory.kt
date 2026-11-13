/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_v2

import io.airbyte.cdk.load.command.aws.AWSAccessKeyConfiguration
import io.airbyte.cdk.load.command.aws.AWSAccessKeyConfigurationProvider
import io.airbyte.cdk.load.command.aws.AWSArnRoleConfiguration
import io.airbyte.cdk.load.command.aws.AWSArnRoleConfigurationProvider
import io.airbyte.cdk.load.command.gcs.GOOGLE_STORAGE_ENDPOINT
import io.airbyte.cdk.load.command.gcs.GcsClientConfiguration
import io.airbyte.cdk.load.command.gcs.GcsHmacKeyConfiguration
import io.airbyte.cdk.load.command.s3.S3BucketConfiguration
import io.airbyte.cdk.load.command.s3.S3BucketConfigurationProvider
import io.airbyte.cdk.load.file.gcs.GcsClient
import io.airbyte.cdk.load.file.gcs.GcsS3Client
import io.airbyte.cdk.load.file.s3.S3ClientFactory

/**
 * Builds a [GcsClient] from a [GcsClientConfiguration] without DI. Used by the checker and test
 * data dumper which need a client built from an explicit config. Synthesizes AWS SDK providers from
 * HMAC credentials and delegates to [S3ClientFactory] via the GCS S3-interop endpoint.
 */
object GcsV2ClientFactory {
    fun make(config: GcsClientConfiguration): GcsClient {
        val credential = config.credential
        return when (credential) {
            is GcsHmacKeyConfiguration ->
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
        }
    }
}
