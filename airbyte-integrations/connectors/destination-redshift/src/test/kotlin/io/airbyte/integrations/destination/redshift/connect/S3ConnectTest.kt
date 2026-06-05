/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.connect

import io.airbyte.integrations.destination.redshift.config.S3StagingConfiguration
import org.junit.jupiter.api.Assertions.assertInstanceOf
import org.junit.jupiter.api.Test
import software.amazon.awssdk.auth.credentials.DefaultCredentialsProvider
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider

class S3ConnectTest {

    private fun s3Config(
        accessKeyId: String? = null,
        secretAccessKey: String? = null,
    ): S3StagingConfiguration =
        S3StagingConfiguration(
            s3BucketName = "bucket",
            s3BucketRegion = "us-east-1",
            accessKeyId = accessKeyId,
            secretAccessKey = secretAccessKey,
        )

    @Test
    fun `uses static credentials when both access key and secret are present`() {
        val provider =
            S3Connect.resolveCredentialsProvider(
                s3Config(accessKeyId = "AKIATEST", secretAccessKey = "secret123")
            )

        assertInstanceOf(StaticCredentialsProvider::class.java, provider)
    }

    @Test
    fun `uses default credentials provider when keys are null`() {
        val provider = S3Connect.resolveCredentialsProvider(s3Config())

        assertInstanceOf(DefaultCredentialsProvider::class.java, provider)
    }

    @Test
    fun `uses default credentials provider when keys are blank strings`() {
        val provider =
            S3Connect.resolveCredentialsProvider(
                s3Config(accessKeyId = "", secretAccessKey = "")
            )

        assertInstanceOf(DefaultCredentialsProvider::class.java, provider)
    }
}
