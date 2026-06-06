/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.config

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertDoesNotThrow
import org.junit.jupiter.api.assertThrows

class S3StagingConfigurationTest {

    @Test
    fun `accepts static credentials when both keys are present`() {
        val config = assertDoesNotThrow {
            S3StagingConfiguration(
                s3BucketName = "bucket",
                s3BucketRegion = "us-east-1",
                accessKeyId = "AKIATEST",
                secretAccessKey = "secret123",
            )
        }
        assertEquals("AKIATEST", config.accessKeyId)
    }

    @Test
    fun `accepts IRSA configuration when both keys are absent`() {
        val config = assertDoesNotThrow {
            S3StagingConfiguration(s3BucketName = "bucket", s3BucketRegion = "us-east-1")
        }
        assertNull(config.accessKeyId)
        assertNull(config.secretAccessKey)
    }

    @Test
    fun `rejects partial credentials with only access key`() {
        assertThrows<IllegalArgumentException> {
            S3StagingConfiguration(
                s3BucketName = "bucket",
                s3BucketRegion = "us-east-1",
                accessKeyId = "AKIATEST",
            )
        }
    }

    @Test
    fun `rejects partial credentials with only secret key`() {
        assertThrows<IllegalArgumentException> {
            S3StagingConfiguration(
                s3BucketName = "bucket",
                s3BucketRegion = "us-east-1",
                secretAccessKey = "secret123",
            )
        }
    }

    @Test
    fun `rejects malformed IAM role ARN`() {
        assertThrows<IllegalArgumentException> {
            S3StagingConfiguration(
                s3BucketName = "bucket",
                s3BucketRegion = "us-east-1",
                iamRoleArn = "not-an-arn",
            )
        }
    }

    @Test
    fun `accepts a well-formed IAM role ARN`() {
        assertDoesNotThrow {
            S3StagingConfiguration(
                s3BucketName = "bucket",
                s3BucketRegion = "us-east-1",
                iamRoleArn = "arn:aws:iam::123456789012:role/redshift-s3-read",
            )
        }
    }
}
