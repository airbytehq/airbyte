/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.connect

import io.airbyte.integrations.destination.redshift.config.RedshiftConfiguration
import io.airbyte.integrations.destination.redshift.config.S3StagingConfiguration
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assumptions.assumeTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows
import software.amazon.awssdk.core.exception.SdkClientException

internal class S3ConnectTest {

    @BeforeEach
    fun requireNoWebIdentityEnv() {
        assumeTrue(System.getenv("AWS_WEB_IDENTITY_TOKEN_FILE") == null)
    }

    private fun config(accessKeyId: String?, secretAccessKey: String?) =
        RedshiftConfiguration(
            host = "redshift.example.com",
            port = 5439,
            database = "mydb",
            schema = "public",
            username = "admin",
            password = "secret",
            jdbcUrlParams = null,
            uploadingMethod =
                S3StagingConfiguration(
                    s3BucketName = "test-bucket",
                    s3BucketRegion = "us-east-1",
                    accessKeyId = accessKeyId,
                    secretAccessKey = secretAccessKey,
                ),
            tunnelMethod = null,
            dropCascade = false,
        )

    @Test
    fun `falls back to static keys when no web identity token is present`() {
        val creds = S3Connect(config("AKID", "SECRET")).createCredentialsProvider().resolveCredentials()

        assertEquals("AKID", creds.accessKeyId())
        assertEquals("SECRET", creds.secretAccessKey())
    }

    @Test
    fun `fails when neither web identity token nor keys are present`() {
        assertThrows<SdkClientException> {
            S3Connect(config(null, null)).createCredentialsProvider().resolveCredentials()
        }
    }
}
