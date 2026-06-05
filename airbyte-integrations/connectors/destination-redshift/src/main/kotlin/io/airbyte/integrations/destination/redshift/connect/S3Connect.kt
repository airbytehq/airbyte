/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.connect

import io.airbyte.integrations.destination.redshift.config.RedshiftConfiguration
import io.airbyte.integrations.destination.redshift.config.S3StagingConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import software.amazon.awssdk.auth.credentials.AwsBasicCredentials
import software.amazon.awssdk.auth.credentials.AwsCredentialsProvider
import software.amazon.awssdk.auth.credentials.DefaultCredentialsProvider
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider
import software.amazon.awssdk.regions.Region
import software.amazon.awssdk.services.s3.S3Client

private val log = KotlinLogging.logger {}

/**
 * Manages S3 client creation for staging operations.
 *
 * Creates an [S3Client] from the S3 staging configuration. When static credentials (access key +
 * secret key) are configured they are used directly; otherwise the AWS [DefaultCredentialsProvider]
 * chain is used, which resolves IRSA / instance-profile / web-identity credentials at runtime.
 */
@Singleton
class S3Connect(private val configuration: RedshiftConfiguration) {

    fun createS3Client(): S3Client {
        val s3Config = configuration.uploadingMethod!!
        val useStaticCredentials =
            !s3Config.accessKeyId.isNullOrBlank() && !s3Config.secretAccessKey.isNullOrBlank()

        log.info {
            "Creating S3 client for bucket '${s3Config.s3BucketName}' " +
                "in region '${s3Config.s3BucketRegion}' using " +
                if (useStaticCredentials) "static credentials"
                else "default credentials provider (IRSA / instance profile)"
        }

        return S3Client.builder()
            .credentialsProvider(resolveCredentialsProvider(s3Config))
            .region(Region.of(s3Config.s3BucketRegion))
            .build()
    }

    companion object {
        /**
         * Selects the AWS credentials provider for the S3 staging client. Static credentials are
         * used only when both the access key and secret are present; otherwise the
         * [DefaultCredentialsProvider] chain resolves IRSA / instance-profile credentials.
         */
        internal fun resolveCredentialsProvider(
            s3Config: S3StagingConfiguration
        ): AwsCredentialsProvider {
            val accessKeyId = s3Config.accessKeyId
            val secretAccessKey = s3Config.secretAccessKey
            return if (!accessKeyId.isNullOrBlank() && !secretAccessKey.isNullOrBlank()) {
                StaticCredentialsProvider.create(
                    AwsBasicCredentials.create(accessKeyId, secretAccessKey)
                )
            } else {
                DefaultCredentialsProvider.create()
            }
        }
    }
}
