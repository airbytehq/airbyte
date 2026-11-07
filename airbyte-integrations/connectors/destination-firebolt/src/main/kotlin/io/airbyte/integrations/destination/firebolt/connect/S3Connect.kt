/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.firebolt.connect

import io.airbyte.integrations.destination.firebolt.config.FireboltConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import software.amazon.awssdk.auth.credentials.AwsBasicCredentials
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider
import software.amazon.awssdk.regions.Region
import software.amazon.awssdk.services.s3.S3Client

private val log = KotlinLogging.logger {}

/** Manages S3 client creation for staging operations. */
@Singleton
class S3Connect(private val configuration: FireboltConfiguration) {

    fun createS3Client(): S3Client {
        val s3Config = configuration.s3Staging!!

        log.info {
            "Creating S3 client for bucket '${s3Config.s3BucketName}' " +
                "in region '${s3Config.s3BucketRegion}'"
        }

        return S3Client.builder()
            .credentialsProvider(
                StaticCredentialsProvider.create(
                    AwsBasicCredentials.create(s3Config.accessKeyId, s3Config.secretAccessKey)
                )
            )
            .region(Region.of(s3Config.s3BucketRegion))
            .build()
    }
}
