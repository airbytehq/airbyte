/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift2.connect

import com.amazonaws.ClientConfiguration
import com.amazonaws.auth.AWSStaticCredentialsProvider
import com.amazonaws.auth.BasicAWSCredentials
import com.amazonaws.retry.RetryMode
import com.amazonaws.services.s3.AmazonS3
import com.amazonaws.services.s3.AmazonS3ClientBuilder
import io.airbyte.integrations.destination.redshift2.config.RedshiftConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton

private val log = KotlinLogging.logger {}

/**
 * Manages S3 client creation for staging operations.
 *
 * Creates an [AmazonS3] client from the S3 staging configuration using static credentials (access
 * key + secret key) and the configured region.
 */
@Singleton
class S3Connect(private val configuration: RedshiftConfiguration) {

    fun createS3Client(): AmazonS3 {
        val s3Config = configuration.uploadingMethod!!

        log.info {
            "Creating S3 client for bucket '${s3Config.s3BucketName}' " +
                "in region '${s3Config.s3BucketRegion}'"
        }

        return AmazonS3ClientBuilder.standard()
            .withCredentials(
                AWSStaticCredentialsProvider(
                    BasicAWSCredentials(s3Config.accessKeyId, s3Config.secretAccessKey)
                ),
            )
            .withClientConfiguration(ClientConfiguration().withRetryMode(RetryMode.STANDARD))
            .withRegion(s3Config.s3BucketRegion)
            .build()
    }
}
