/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.connect

import io.airbyte.integrations.destination.redshift.config.RedshiftConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import software.amazon.awssdk.auth.credentials.AwsBasicCredentials
import software.amazon.awssdk.auth.credentials.AwsCredentialsProvider
import software.amazon.awssdk.auth.credentials.AwsCredentialsProviderChain
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider
import software.amazon.awssdk.auth.credentials.WebIdentityTokenFileCredentialsProvider
import software.amazon.awssdk.regions.Region
import software.amazon.awssdk.services.s3.S3Client

private val log = KotlinLogging.logger {}

/**
 * Manages AWS credentials and S3 client creation for staging operations.
 *
 * Credentials are resolved in order:
 * 1. OIDC web identity token (`AWS_WEB_IDENTITY_TOKEN_FILE` + `AWS_ROLE_ARN` env vars), exchanged
 *    for temporary credentials via STS AssumeRoleWithWebIdentity.
 * 2. Static access key + secret key from the S3 staging configuration, if provided.
 */
@Singleton
class S3Connect(private val configuration: RedshiftConfiguration) {

    fun createCredentialsProvider(): AwsCredentialsProvider {
        val s3Config = configuration.uploadingMethod!!
        val providers = mutableListOf<AwsCredentialsProvider>(
            WebIdentityTokenFileCredentialsProvider.create(),
        )
        if (!s3Config.accessKeyId.isNullOrBlank() && !s3Config.secretAccessKey.isNullOrBlank()) {
            providers.add(
                StaticCredentialsProvider.create(
                    AwsBasicCredentials.create(s3Config.accessKeyId, s3Config.secretAccessKey),
                ),
            )
        }
        return AwsCredentialsProviderChain.builder().credentialsProviders(providers).build()
    }

    fun createS3Client(
        credentialsProvider: AwsCredentialsProvider = createCredentialsProvider()
    ): S3Client {
        val s3Config = configuration.uploadingMethod!!

        log.info {
            "Creating S3 client for bucket '${s3Config.s3BucketName}' " +
                "in region '${s3Config.s3BucketRegion}'"
        }

        return S3Client.builder()
            .credentialsProvider(credentialsProvider)
            .region(Region.of(s3Config.s3BucketRegion))
            .build()
    }
}
