/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.connect

import io.airbyte.integrations.destination.redshift.config.RedshiftConfiguration
import io.airbyte.integrations.destination.redshift.config.S3AuthMode
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import software.amazon.awssdk.auth.credentials.AwsBasicCredentials
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider
import software.amazon.awssdk.regions.Region
import software.amazon.awssdk.services.s3.S3Client

private val log = KotlinLogging.logger {}

/**
 * Manages S3 client creation for staging operations.
 *
 * Creates an [S3Client] from the S3 staging configuration using static credentials when an access
 * key is configured. Otherwise no provider is set, so the SDK resolves (and owns) the AWS default
 * credential chain (environment, instance profile, IAM role for service accounts, ...).
 */
@Singleton
class S3Connect(private val configuration: RedshiftConfiguration) {

    fun createS3Client(): S3Client {
        val s3Config = configuration.uploadingMethod!!
        val authMode = s3Config.authMode

        log.info {
            "Creating S3 client for bucket '${s3Config.s3BucketName}' " +
                "in region '${s3Config.s3BucketRegion}' using " +
                if (authMode is S3AuthMode.StaticCredentials) "static credentials"
                else "the AWS default credential chain"
        }

        val builder = S3Client.builder().region(Region.of(s3Config.s3BucketRegion))
        if (authMode is S3AuthMode.StaticCredentials) {
            builder.credentialsProvider(
                StaticCredentialsProvider.create(
                    AwsBasicCredentials.create(authMode.accessKeyId, authMode.secretAccessKey)
                )
            )
        }
        return builder.build()
    }
}
