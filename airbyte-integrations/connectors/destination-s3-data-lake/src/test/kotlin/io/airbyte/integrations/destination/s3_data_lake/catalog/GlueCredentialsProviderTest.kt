/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake.catalog

import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertDoesNotThrow
import org.junit.jupiter.api.assertThrows
import software.amazon.awssdk.auth.credentials.AwsCredentialsProvider
import software.amazon.awssdk.auth.credentials.DefaultCredentialsProvider
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider
import software.amazon.awssdk.services.sts.auth.StsAssumeRoleCredentialsProvider

internal class GlueCredentialsProviderTest {

    private fun delegateOf(provider: AwsCredentialsProvider): Any? {
        val delegateField = GlueCredentialsProvider::class.java.getDeclaredField("delegate")
        delegateField.isAccessible = true
        return delegateField.get(provider)
    }

    @Test
    fun `static creds mode returns a provider when keys are present`() {
        val provider =
            GlueCredentialsProvider.create(
                mapOf(
                    AWS_CREDENTIALS_MODE to AWS_CREDENTIALS_MODE_STATIC_CREDS,
                    ACCESS_KEY_ID to "key",
                    SECRET_ACCESS_KEY to "secret",
                ),
            )
        Assertions.assertInstanceOf(StaticCredentialsProvider::class.java, delegateOf(provider))
    }

    @Test
    fun `static creds mode falls back to default chain when keys are missing`() {
        // Building should not throw even though no access keys are present.
        val provider = assertDoesNotThrow {
            GlueCredentialsProvider.create(
                mapOf(AWS_CREDENTIALS_MODE to AWS_CREDENTIALS_MODE_STATIC_CREDS),
            )
        }
        Assertions.assertInstanceOf(DefaultCredentialsProvider::class.java, delegateOf(provider))
    }

    @Test
    fun `assume role mode returns an STS-backed provider when system keys are present`() {
        val provider =
            GlueCredentialsProvider.create(
                mapOf(
                    AWS_CREDENTIALS_MODE to AWS_CREDENTIALS_MODE_ASSUME_ROLE,
                    ACCESS_KEY_ID to "key",
                    SECRET_ACCESS_KEY to "secret",
                    ASSUME_ROLE_ARN to "arn:aws:iam::123456789012:role/test",
                    ASSUME_ROLE_EXTERNAL_ID to "ext",
                    ASSUME_ROLE_REGION to "us-east-1",
                ),
            )
        Assertions.assertInstanceOf(
            StsAssumeRoleCredentialsProvider::class.java,
            delegateOf(provider),
        )
    }

    @Test
    fun `assume role mode falls back to default chain for the STS client when system keys are missing`() {
        // Reproduces the privatelink / IRSA scenario where the connector pod has
        // no system-provided static keys to bootstrap the STS client. Building
        // the provider must not NPE on AwsBasicCredentials.create(null, null);
        // instead the STS client should be configured with the default chain so
        // it can use the pod's IAM identity to perform AssumeRole.
        assertDoesNotThrow {
            GlueCredentialsProvider.create(
                mapOf(
                    AWS_CREDENTIALS_MODE to AWS_CREDENTIALS_MODE_ASSUME_ROLE,
                    ASSUME_ROLE_ARN to "arn:aws:iam::123456789012:role/test",
                    ASSUME_ROLE_REGION to "us-east-1",
                ),
            )
        }
    }

    @Test
    fun `assume role mode falls back to default chain when system keys are blank`() {
        // AwsBasicCredentials trims internally and rejects blanks, so an empty-string
        // key passes a plain null check but still fails. Deployments hit this because
        // the assume-role properties default to "" rather than being absent.
        assertDoesNotThrow {
            GlueCredentialsProvider.create(
                mapOf(
                    AWS_CREDENTIALS_MODE to AWS_CREDENTIALS_MODE_ASSUME_ROLE,
                    ACCESS_KEY_ID to "",
                    SECRET_ACCESS_KEY to "",
                    ASSUME_ROLE_ARN to "arn:aws:iam::123456789012:role/test",
                    ASSUME_ROLE_REGION to "us-east-1",
                ),
            )
        }
    }

    @Test
    fun `static creds mode falls back to default chain when keys are blank`() {
        val provider = assertDoesNotThrow {
            GlueCredentialsProvider.create(
                mapOf(
                    AWS_CREDENTIALS_MODE to AWS_CREDENTIALS_MODE_STATIC_CREDS,
                    ACCESS_KEY_ID to "",
                    SECRET_ACCESS_KEY to "",
                ),
            )
        }
        Assertions.assertInstanceOf(DefaultCredentialsProvider::class.java, delegateOf(provider))
    }

    @Test
    fun `unknown mode raises a descriptive error`() {
        val error =
            assertThrows<IllegalArgumentException> {
                GlueCredentialsProvider.create(mapOf(AWS_CREDENTIALS_MODE to "bogus"))
            }
        Assertions.assertTrue(error.message!!.contains("bogus"))
    }

    // Sanity check that the underlying STS provider type is what we expect, so
    // future refactors that swap the implementation are caught loudly.
    @Test
    fun `assume role mode delegates to StsAssumeRoleCredentialsProvider`() {
        val provider =
            GlueCredentialsProvider.create(
                mapOf(
                    AWS_CREDENTIALS_MODE to AWS_CREDENTIALS_MODE_ASSUME_ROLE,
                    ASSUME_ROLE_ARN to "arn:aws:iam::123456789012:role/test",
                    ASSUME_ROLE_REGION to "us-east-1",
                ),
            )
        Assertions.assertInstanceOf(
            StsAssumeRoleCredentialsProvider::class.java,
            delegateOf(provider),
        )
    }
}
