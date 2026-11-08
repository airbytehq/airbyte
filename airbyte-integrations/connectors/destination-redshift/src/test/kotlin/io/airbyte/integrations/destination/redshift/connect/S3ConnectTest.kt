/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.connect

import io.airbyte.integrations.destination.redshift.config.RedshiftConfiguration
import io.airbyte.integrations.destination.redshift.config.S3StagingConfiguration
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows
import software.amazon.awssdk.auth.credentials.AwsCredentialsProvider
import software.amazon.awssdk.auth.credentials.AwsSessionCredentials
import software.amazon.awssdk.core.exception.SdkClientException

internal class S3ConnectTest {

    /** Stands in for a pod with `AWS_WEB_IDENTITY_TOKEN_FILE` + `AWS_ROLE_ARN` set. */
    private val webIdentityAvailable = AwsCredentialsProvider {
        AwsSessionCredentials.create("ASIA_ROLE", "ROLE_SECRET", "ROLE_TOKEN")
    }

    /** Stands in for a pod without a web identity token. */
    private val webIdentityUnavailable = AwsCredentialsProvider {
        throw SdkClientException.create("AWS_WEB_IDENTITY_TOKEN_FILE is not set")
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
    fun `uses web identity credentials when no keys are configured`() {
        val creds =
            S3Connect(config(null, null))
                .createCredentialsProvider(webIdentityAvailable)
                .resolveCredentials()

        assertEquals("ASIA_ROLE", creds.accessKeyId())
        assertEquals("ROLE_SECRET", creds.secretAccessKey())
        assertTrue(creds is AwsSessionCredentials)
        assertEquals("ROLE_TOKEN", (creds as AwsSessionCredentials).sessionToken())
    }

    @Test
    fun `treats blank keys as not configured`() {
        val creds =
            S3Connect(config("", " "))
                .createCredentialsProvider(webIdentityAvailable)
                .resolveCredentials()

        assertEquals("ASIA_ROLE", creds.accessKeyId())
    }

    @Test
    fun `uses configured keys when web identity is unavailable`() {
        val creds =
            S3Connect(config("AKID", "SECRET"))
                .createCredentialsProvider(webIdentityUnavailable)
                .resolveCredentials()

        assertEquals("AKID", creds.accessKeyId())
        assertEquals("SECRET", creds.secretAccessKey())
    }

    @Test
    fun `configured keys take precedence over web identity`() {
        val creds =
            S3Connect(config("AKID", "SECRET"))
                .createCredentialsProvider(webIdentityAvailable)
                .resolveCredentials()

        assertEquals("AKID", creds.accessKeyId())
        assertEquals("SECRET", creds.secretAccessKey())
    }

    @Test
    fun `fails when neither web identity token nor keys are present`() {
        assertThrows<SdkClientException> {
            S3Connect(config(null, null))
                .createCredentialsProvider(webIdentityUnavailable)
                .resolveCredentials()
        }
    }
}
