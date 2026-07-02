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
 * Builds a [GcsClient] directly from a [GcsClientConfiguration], without going through the
 * DI-scoped `GcsClientFactory` bean.
 *
 * The main load pipeline injects the CDK's `GcsClientFactory` bean; but the [DestinationChecker]
 * contract and the integration-test data dumper must build the client from a config passed in by
 * hand ("do not inject configuration"). `destination-s3` solves the same problem with
 * [S3ClientFactory.make]. GCS talks to Google Cloud Storage over its S3-interoperability endpoint,
 * so we synthesize the AWS access-key / bucket providers from the HMAC credentials, build the CDK's
 * [S3ClientFactory], and wrap it in [GcsS3Client] — exactly what the CDK bean does internally.
 *
 * This lives in the connector (rather than as a companion on the CDK's `GcsClientFactory`) so the
 * migration is a single connector-only change: it uses only published CDK APIs and touches no
 * `airbyte-cdk` module.
 */
object GcsV2ClientFactory {
    fun make(config: GcsClientConfiguration): GcsClient {
        // Bind to a local val so the smart-cast below works: config.credential is a public API
        // property from the CDK module and cannot be smart-cast directly.
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
